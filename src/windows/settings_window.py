from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QCheckBox, QGroupBox,
                             QSpinBox, QComboBox, QTabWidget, QSlider, QGridLayout,
                             QTextBrowser, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QDialog, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from src.utils.settings_manager import settings_manager
from src.utils.version import get_version_string, get_full_version_info, APP_NAME, APP_DESCRIPTION
from src.utils.icon_helper import get_application_icon
from src.windows.gesture_mapping_dialog import GestureMappingDialog
from src.core.system_control import SystemController
from src.utils.gesture_names import get_gesture_display_name, get_gesture_english_name


class SettingsWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCGCA-Lite 设置")
        self.setMinimumSize(500, 400)
        self.setWindowIcon(get_application_icon())

        # 存储原始设置值，用于检测变更
        self._original_values = {}
        self._is_modified = False

        self.init_ui()
        self.load_settings()
        self.connect_change_signals()

    def init_ui(self):
        layout = QVBoxLayout()

        # 创建标签页
        tabs = QTabWidget()
        tabs.addTab(self.create_general_tab(), "常规")
        tabs.addTab(self.create_display_tab(), "显示")
        tabs.addTab(self.create_gesture_tab(), "手势控制")
        tabs.addTab(self.create_help_tab(), "帮助")
        tabs.addTab(self.create_about_tab(), "关于")

        layout.addWidget(tabs)

        # 底部按钮
        button_layout = QHBoxLayout()

        # 左侧：恢复默认按钮
        self.default_btn = QPushButton("恢复默认")
        self.default_btn.clicked.connect(self.restore_defaults)
        button_layout.addWidget(self.default_btn)

        button_layout.addStretch()

        # 右侧：保存、重置、关闭按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.setEnabled(False)  # 初始状态禁用
        self.save_btn.clicked.connect(self.save_settings)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setEnabled(False)  # 初始状态禁用
        self.reset_btn.clicked.connect(self.reset_settings)

        cancel_btn = QPushButton("关闭")
        cancel_btn.clicked.connect(self.close)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # 启动设置
        startup_group = QGroupBox("启动设置")
        startup_layout = QVBoxLayout()

        self.auto_start_cb = QCheckBox("开机自动启动")
        self.show_splash_cb = QCheckBox("显示启动动画")
        self.show_splash_cb.setChecked(True)

        startup_layout.addWidget(self.auto_start_cb)
        startup_layout.addWidget(self.show_splash_cb)
        startup_group.setLayout(startup_layout)

        layout.addWidget(startup_group)

        # 截图设置
        screenshot_group = QGroupBox("截图设置")
        screenshot_layout = QVBoxLayout()

        # 截图保存路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("保存路径:"))
        self.screenshot_path_edit = QLineEdit()
        self.screenshot_path_edit.setReadOnly(True)
        self.screenshot_path_edit.setPlaceholderText("默认: Pictures\\VCGCA-Screenshots")
        path_layout.addWidget(self.screenshot_path_edit)

        self.browse_path_btn = QPushButton("浏览...")
        self.browse_path_btn.clicked.connect(self.browse_screenshot_path)
        path_layout.addWidget(self.browse_path_btn)

        self.reset_path_btn = QPushButton("恢复默认")
        self.reset_path_btn.clicked.connect(self.reset_screenshot_path)
        path_layout.addWidget(self.reset_path_btn)

        screenshot_layout.addLayout(path_layout)

        self.copy_to_clipboard_cb = QCheckBox("截图后复制到剪贴板")
        self.copy_to_clipboard_cb.setChecked(False)
        self.copy_to_clipboard_cb.setToolTip("截图成功后自动将图片复制到剪贴板")
        screenshot_layout.addWidget(self.copy_to_clipboard_cb)

        # 托盘菜单设置
        self.show_open_folder_cb = QCheckBox("在托盘菜单显示'打开截图文件夹'")
        self.show_open_folder_cb.setChecked(True)
        self.show_open_folder_cb.setToolTip("在任务栏图标右键菜单中显示打开截图文件夹的选项")
        screenshot_layout.addWidget(self.show_open_folder_cb)

        screenshot_group.setLayout(screenshot_layout)

        layout.addWidget(screenshot_group)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_display_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # HUD设置
        hud_group = QGroupBox("HUD 设置")
        hud_layout = QVBoxLayout()

        # 尺寸设置（使用统一的网格布局）
        size_layout = QGridLayout()
        size_layout.setColumnStretch(2, 1)  # 让第3列拉伸，保持对齐

        # 透明度
        size_layout.addWidget(QLabel("透明度:"), 0, 0)
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(20, 100)
        self.opacity_spin.setValue(80)
        self.opacity_spin.setSuffix("%")
        size_layout.addWidget(self.opacity_spin, 0, 1)

        # 宽度
        size_layout.addWidget(QLabel("宽度:"), 1, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 600)
        self.width_spin.setValue(300)
        self.width_spin.setSuffix(" px")
        size_layout.addWidget(self.width_spin, 1, 1)

        # 高度
        size_layout.addWidget(QLabel("高度:"), 2, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 400)
        self.height_spin.setValue(150)
        self.height_spin.setSuffix(" px")
        size_layout.addWidget(self.height_spin, 2, 1)

        hud_layout.addLayout(size_layout)

        hud_layout.addSpacing(10)

        # 水平位置滑动条
        h_pos_layout = QVBoxLayout()
        h_pos_header = QHBoxLayout()
        h_pos_header.addWidget(QLabel("水平位置:"))
        self.h_pos_label = QLabel("50% (居中)")
        self.h_pos_label.setStyleSheet("color: #3498db; font-weight: bold;")
        h_pos_header.addWidget(self.h_pos_label)
        h_pos_header.addStretch()
        h_pos_layout.addLayout(h_pos_header)

        self.h_pos_slider = QSlider(Qt.Orientation.Horizontal)
        self.h_pos_slider.setRange(0, 100)
        self.h_pos_slider.setValue(50)
        self.h_pos_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.h_pos_slider.setTickInterval(10)
        self.h_pos_slider.valueChanged.connect(self.on_h_pos_changed)
        h_pos_layout.addWidget(self.h_pos_slider)

        # 添加刻度标签
        h_ticks_layout = QHBoxLayout()
        h_ticks_layout.addWidget(QLabel("左"))
        h_ticks_layout.addStretch()
        h_ticks_layout.addWidget(QLabel("中"))
        h_ticks_layout.addStretch()
        h_ticks_layout.addWidget(QLabel("右"))
        h_pos_layout.addLayout(h_ticks_layout)

        hud_layout.addLayout(h_pos_layout)

        hud_layout.addSpacing(10)

        # 垂直位置滑动条
        v_pos_layout = QVBoxLayout()
        v_pos_header = QHBoxLayout()
        v_pos_header.addWidget(QLabel("垂直位置:"))
        self.v_pos_label = QLabel("0% (顶部)")
        self.v_pos_label.setStyleSheet("color: #3498db; font-weight: bold;")
        v_pos_header.addWidget(self.v_pos_label)
        v_pos_header.addStretch()
        v_pos_layout.addLayout(v_pos_header)

        self.v_pos_slider = QSlider(Qt.Orientation.Horizontal)
        self.v_pos_slider.setRange(0, 100)
        self.v_pos_slider.setValue(0)
        self.v_pos_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.v_pos_slider.setTickInterval(10)
        self.v_pos_slider.valueChanged.connect(self.on_v_pos_changed)
        v_pos_layout.addWidget(self.v_pos_slider)

        # 添加刻度标签
        v_ticks_layout = QHBoxLayout()
        v_ticks_layout.addWidget(QLabel("上"))
        v_ticks_layout.addStretch()
        v_ticks_layout.addWidget(QLabel("中"))
        v_ticks_layout.addStretch()
        v_ticks_layout.addWidget(QLabel("下"))
        v_pos_layout.addLayout(v_ticks_layout)

        hud_layout.addLayout(v_pos_layout)

        hud_group.setLayout(hud_layout)
        layout.addWidget(hud_group)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def browse_screenshot_path(self):
        """浏览选择截图保存路径"""
        current_path = self.screenshot_path_edit.text()
        if not current_path:
            current_path = str(Path.home() / "Pictures" / "VCGCA-Screenshots")

        folder = QFileDialog.getExistingDirectory(
            self,
            "选择截图保存文件夹",
            current_path,
            QFileDialog.Option.ShowDirsOnly
        )

        if folder:
            self.screenshot_path_edit.setText(folder)
            self.on_value_changed()

    def reset_screenshot_path(self):
        """恢复默认截图保存路径"""
        self.screenshot_path_edit.clear()
        self.on_value_changed()

    def get_screenshot_path(self):
        """获取截图保存路径（自定义或默认）"""
        custom_path = self.screenshot_path_edit.text()
        if custom_path:
            return custom_path
        return str(Path.home() / "Pictures" / "VCGCA-Screenshots")

    def on_h_pos_changed(self, value):
        """水平位置变化"""
        if value == 0:
            text = "0% (最左)"
        elif value == 50:
            text = "50% (居中)"
        elif value == 100:
            text = "100% (最右)"
        else:
            text = f"{value}%"
        self.h_pos_label.setText(text)
        self.on_value_changed()

    def on_v_pos_changed(self, value):
        """垂直位置变化"""
        if value == 0:
            text = "0% (顶部)"
        elif value == 50:
            text = "50% (居中)"
        elif value == 100:
            text = "100% (底部)"
        else:
            text = f"{value}%"
        self.v_pos_label.setText(text)
        self.on_value_changed()

    def create_gesture_tab(self):
        """创建手势控制标签页"""
        tab = QWidget()
        layout = QVBoxLayout()

        # 时间设置区域（横向排列）
        time_group = QGroupBox("时间设置")
        time_layout = QHBoxLayout()

        # 准备时间
        prepare_time_layout = QVBoxLayout()
        prepare_time_layout.addWidget(QLabel("准备时间:"))
        self.prepare_time_spin = QSpinBox()
        self.prepare_time_spin.setRange(100, 5000)
        self.prepare_time_spin.setValue(500)
        self.prepare_time_spin.setSuffix(" ms")
        prepare_time_layout.addWidget(self.prepare_time_spin)
        time_layout.addLayout(prepare_time_layout)

        time_layout.addSpacing(20)

        # 变化时间
        change_time_layout = QVBoxLayout()
        change_time_layout.addWidget(QLabel("变化时间:"))
        self.change_time_spin = QSpinBox()
        self.change_time_spin.setRange(100, 5000)
        self.change_time_spin.setValue(1000)
        self.change_time_spin.setSuffix(" ms")
        change_time_layout.addWidget(self.change_time_spin)
        time_layout.addLayout(change_time_layout)

        time_layout.addSpacing(20)

        # 冷静时间
        cooldown_time_layout = QVBoxLayout()
        cooldown_time_layout.addWidget(QLabel("冷静时间:"))
        self.cooldown_time_spin = QSpinBox()
        self.cooldown_time_spin.setRange(0, 10000)
        self.cooldown_time_spin.setValue(2000)
        self.cooldown_time_spin.setSuffix(" ms")
        cooldown_time_layout.addWidget(self.cooldown_time_spin)
        time_layout.addLayout(cooldown_time_layout)

        time_layout.addStretch()
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        # 控制功能映射表
        mapping_group = QGroupBox("手势控制功能映射")
        mapping_layout = QVBoxLayout()

        # 创建表格
        self.gesture_mapping_table = QTableWidget()
        self.gesture_mapping_table.setColumnCount(3)
        self.gesture_mapping_table.setHorizontalHeaderLabels(["准备手势", "响应手势", "控制功能"])
        self.gesture_mapping_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.gesture_mapping_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.gesture_mapping_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.gesture_mapping_table.setAlternatingRowColors(True)

        # 添加示例数据
        self._load_gesture_mappings()

        mapping_layout.addWidget(self.gesture_mapping_table)

        # 表格操作按钮
        table_btn_layout = QHBoxLayout()
        self.add_mapping_btn = QPushButton("添加映射")
        self.add_mapping_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.add_mapping_btn.clicked.connect(self.add_gesture_mapping)

        self.edit_mapping_btn = QPushButton("编辑")
        self.edit_mapping_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.edit_mapping_btn.clicked.connect(self.edit_gesture_mapping)

        self.delete_mapping_btn = QPushButton("删除")
        self.delete_mapping_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        self.delete_mapping_btn.clicked.connect(self.delete_gesture_mapping)

        table_btn_layout.addWidget(self.add_mapping_btn)
        table_btn_layout.addWidget(self.edit_mapping_btn)
        table_btn_layout.addWidget(self.delete_mapping_btn)
        table_btn_layout.addStretch()

        mapping_layout.addLayout(table_btn_layout)
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _load_gesture_mappings(self):
        """加载手势映射到表格（默认数据）"""
        # 默认示例数据 - 使用action_key
        default_mappings = [
            {"prepare": "Open_Palm", "response": "Closed_Fist", "action": "screenshot"},
            {"prepare": "Open_Palm", "response": "Thumb_Up", "action": "volume_up"},
            {"prepare": "Open_Palm", "response": "Thumb_Down", "action": "volume_down"},
            {"prepare": "Victory", "response": "Pointing_Up", "action": "show_desktop"},
        ]
        self._load_gesture_mappings_from_settings(default_mappings)

    def _load_gesture_mappings_from_settings(self, mappings):
        """从设置加载手势映射到表格"""
        if not mappings:
            self._load_gesture_mappings()
            return

        self.gesture_mapping_table.setRowCount(len(mappings))
        for row, mapping in enumerate(mappings):
            # 将英文手势名称转换为中文显示
            prepare_english = mapping.get("prepare", "")
            response_english = mapping.get("response", "")
            self.gesture_mapping_table.setItem(row, 0, QTableWidgetItem(get_gesture_display_name(prepare_english)))
            self.gesture_mapping_table.setItem(row, 1, QTableWidgetItem(get_gesture_display_name(response_english)))
            # 将action_key转换为显示名称
            action_key = mapping.get("action", "")
            action_display = SystemController.get_action_display_name(action_key)
            self.gesture_mapping_table.setItem(row, 2, QTableWidgetItem(action_display))

    def _get_gesture_mappings_from_table(self):
        """从表格获取手势映射数据"""
        mappings = []
        for row in range(self.gesture_mapping_table.rowCount()):
            # 表格中存储的是中文手势名称，需要转换回英文
            prepare_display = self.gesture_mapping_table.item(row, 0).text() if self.gesture_mapping_table.item(row, 0) else ""
            response_display = self.gesture_mapping_table.item(row, 1).text() if self.gesture_mapping_table.item(row, 1) else ""
            prepare = get_gesture_english_name(prepare_display)
            response = get_gesture_english_name(response_display)
            # 表格中存储的是显示名称，需要查找对应的action_key
            action_display = self.gesture_mapping_table.item(row, 2).text() if self.gesture_mapping_table.item(row, 2) else ""
            # 通过显示名称查找key
            action_key = None
            for key, display in SystemController.AVAILABLE_ACTIONS.items():
                if display == action_display:
                    action_key = key
                    break
            if action_key:
                mappings.append({"prepare": prepare, "response": response, "action": action_key})
        return mappings

    def add_gesture_mapping(self):
        """添加新的手势映射"""
        dialog = GestureMappingDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            row = self.gesture_mapping_table.rowCount()
            self.gesture_mapping_table.insertRow(row)
            # 将英文手势名称转换为中文显示
            self.gesture_mapping_table.setItem(row, 0, QTableWidgetItem(get_gesture_display_name(data["prepare"])))
            self.gesture_mapping_table.setItem(row, 1, QTableWidgetItem(get_gesture_display_name(data["response"])))
            # 将action_key转换为显示名称显示在表格中
            action_display = SystemController.get_action_display_name(data["action"])
            self.gesture_mapping_table.setItem(row, 2, QTableWidgetItem(action_display))
            self.on_value_changed()

    def edit_gesture_mapping(self):
        """编辑选中的手势映射"""
        current_row = self.gesture_mapping_table.currentRow()
        if current_row >= 0:
            # 获取当前行的数据（中文显示名称）
            prepare_display = self.gesture_mapping_table.item(current_row, 0).text() if self.gesture_mapping_table.item(current_row, 0) else ""
            response_display = self.gesture_mapping_table.item(current_row, 1).text() if self.gesture_mapping_table.item(current_row, 1) else ""
            # 转换为英文名称传递给对话框
            prepare = get_gesture_english_name(prepare_display)
            response = get_gesture_english_name(response_display)
            # 表格中存储的是显示名称，需要查找对应的action_key
            action_display = self.gesture_mapping_table.item(current_row, 2).text() if self.gesture_mapping_table.item(current_row, 2) else ""
            action_key = None
            for key, display in SystemController.AVAILABLE_ACTIONS.items():
                if display == action_display:
                    action_key = key
                    break

            # 打开编辑对话框
            dialog = GestureMappingDialog(self, prepare, response, action_key)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                # 将英文手势名称转换为中文显示
                self.gesture_mapping_table.setItem(current_row, 0, QTableWidgetItem(get_gesture_display_name(data["prepare"])))
                self.gesture_mapping_table.setItem(current_row, 1, QTableWidgetItem(get_gesture_display_name(data["response"])))
                # 将action_key转换为显示名称显示在表格中
                new_action_display = SystemController.get_action_display_name(data["action"])
                self.gesture_mapping_table.setItem(current_row, 2, QTableWidgetItem(new_action_display))
                self.on_value_changed()

    def delete_gesture_mapping(self):
        """删除选中的手势映射"""
        current_row = self.gesture_mapping_table.currentRow()
        if current_row >= 0:
            self.gesture_mapping_table.removeRow(current_row)
            self.on_value_changed()

    def create_help_tab(self):
        """创建帮助标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # 创建帮助内容浏览器
        help_browser = QTextBrowser()
        help_browser.setOpenExternalLinks(True)
        help_browser.setHtml("""
        <html>
        <head>
            <style>
                body { font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; font-size: 13px; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 8px; font-size: 16px; }
                h3 { color: #333; margin-top: 15px; font-size: 14px; }
                .section { background: #f8f9fa; padding: 12px; margin: 10px 0; border-radius: 6px; border-left: 3px solid #2196F3; }
                .gesture { background: #fff3e0; padding: 8px; margin: 5px 0; border-radius: 4px; }
                .tip { background: #e8f5e9; padding: 10px; margin: 10px 0; border-left: 3px solid #4CAF50; border-radius: 4px; }
                ul { margin: 8px 0; padding-left: 20px; }
                li { margin: 4px 0; }
                code { background: #f5f5f5; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
            </style>
        </head>
        <body>
            <h2>📚 使用指南</h2>

            <div class="section">
                <h3>启动程序</h3>
                <p>双击 VCGCA-Lite.exe 启动，程序会在系统托盘显示图标。</p>
            </div>

            <div class="section">
                <h3>基本使用流程</h3>
                <ol>
                    <li>确保摄像头正常工作</li>
                    <li>在摄像头前做出准备手势（详见下方手势说明）</li>
                    <li>保持手势稳定约1秒，HUD显示"就绪"</li>
                    <li>快速切换到响应手势</li>
                    <li>成功触发映射时，HUD显示触发的"动作名"</li>
                </ol>
            </div>

            <div class="section">
                <h3>系统托盘菜单</h3>
                <p>右键点击托盘图标可以：</p>
                <ul>
                    <li><strong>显示设置</strong> - 打开此设置窗口</li>
                    <li><strong>启用/禁用HUD提示</strong> - 切换屏幕提示</li>
                    <li><strong>显示调试窗口</strong> - 查看摄像头画面</li>
                    <li><strong>查看日志</strong> - 打开日志查看器</li>
                    <li><strong>打开截图文件夹</strong> - 可在设置中显示或隐藏该功能</li>
                    <li><strong>退出</strong> - 关闭程序</li>
                </ul>
            </div>

            <h2>👋 手势说明</h2>
            <p>所有手势都需要保持<strong>准备时间</strong>默认0.8秒才能触发。</p>

            <div class="gesture">
                <strong>✌️ 剪刀手</strong> - 伸出食指和中指形成"V"字
            </div>
            <div class="gesture">
                <strong>👍 点赞</strong> - 竖起大拇指，其他四指握拳
            </div>
            <div class="gesture">
                <strong>👎 点踩</strong> - 大拇指向下，其他四指握拳
            </div>
            <div class="gesture">
                <strong>☝️ 食指指天</strong> - 食指向上伸直，其他手指握拳
            </div>
            <div class="gesture">
                <strong>✊ 握拳</strong> - 五指全部弯曲握拳
            </div>
            <div class="gesture">
                <strong>🖐️ 张开手掌</strong> - 五指伸直张开
            </div>

            <div class="tip">
                <strong>💡 提示</strong><br>
                确保光线充足，手势距离摄像头 30-80 厘米最佳。
            </div>

            <h2>⚙️ 设置说明</h2>

            <div class="section">
                <h3>常规设置</h3>
                <ul>
                    <li><strong>开机自动启动</strong> - Windows 启动时自动运行</li>
                    <li><strong>显示启动动画</strong> - 启动时显示欢迎画面</li>
                    <li><strong>截图后复制到剪贴板</strong> - 截图成功后自动复制到剪贴板</li>
                </ul>
            </div>

            <div class="section">
                <h3>显示设置</h3>
                <ul>
                    <li><strong>透明度/宽度/高度</strong> - HUD 窗口外观</li>
                    <li><strong>水平/垂直位置</strong> - HUD 窗口位置</li>
                </ul>
            </div>

            <div class="section">
                <h3>手势控制设置</h3>
                <ul>
                    <li><strong>准备时间</strong> - 手势保持时间，防止误触发</li>
                    <li><strong>变化时间</strong> - 手势变化检测时间</li>
                    <li><strong>冷静时间</strong> - 两次成功控制之间的间隔</li>
                    <li><strong>手势映射</strong> - 配置手势与控制功能的对应关系</li>
                </ul>
            </div>

            <h2>❓ 常见问题</h2>

            <div class="section">
                <p><strong>Q: 程序无法启动？</strong></p>
                <p>A: 请检查摄像头驱动，或尝试以管理员身份运行。</p>
            </div>

            <div class="section">
                <p><strong>Q: 手势无法识别？</strong></p>
                <p>A: 确保光线充足，手势清晰可见。可在调试窗口查看识别状态。</p>
            </div>

            <div class="section">
                <p><strong>Q: 截图保存在哪里？</strong></p>
                <p>A: 默认保存在用户目录下的 Pictures\Screenshots 文件夹中。</p>
            </div>
        </body>
        </html>
        """)

        layout.addWidget(help_browser)

        tab.setLayout(layout)
        return tab

    def create_about_tab(self):
        """创建关于标签页"""
        tab = QWidget()
        layout = QVBoxLayout()

        # 获取版本信息
        version_info = get_full_version_info()

        # 应用信息组
        app_group = QGroupBox("应用信息")
        app_layout = QVBoxLayout()

        # 应用名称和版本
        name_label = QLabel(f"<h2>{version_info['app_display_name']}</h2>")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_layout.addWidget(name_label)

        version_label = QLabel(f"<h3>版本 {version_info['version']}</h3>")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #3498db;")
        app_layout.addWidget(version_label)

        # 描述
        desc_label = QLabel(version_info['description'])
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #7f8c8d; margin: 10px;")
        app_layout.addWidget(desc_label)

        app_group.setLayout(app_layout)
        layout.addWidget(app_group)

        # 详细信息组
        info_group = QGroupBox("详细信息")
        info_layout = QGridLayout()

        row = 0
        info_items = [
            ("开发者:", version_info['developer']),
            ("公司:", version_info['company']),
            ("构建日期:", version_info['build_date']),
            ("许可证:", version_info['license']),
        ]

        for label_text, value in info_items:
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            info_layout.addWidget(label, row, 0)
            info_layout.addWidget(QLabel(value), row, 1)
            row += 1

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 版权信息
        copyright_label = QLabel(version_info['copyright'])
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #95a5a6; margin-top: 10px;")
        layout.addWidget(copyright_label)

        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def connect_change_signals(self):
        """连接所有控件的变更信号"""
        # 常规设置
        self.auto_start_cb.stateChanged.connect(self.on_value_changed)
        self.show_splash_cb.stateChanged.connect(self.on_value_changed)
        self.copy_to_clipboard_cb.stateChanged.connect(self.on_value_changed)
        self.show_open_folder_cb.stateChanged.connect(self.on_value_changed)

        # 显示设置
        self.opacity_spin.valueChanged.connect(self.on_value_changed)
        self.width_spin.valueChanged.connect(self.on_value_changed)
        self.height_spin.valueChanged.connect(self.on_value_changed)

        # 手势控制设置
        self.prepare_time_spin.valueChanged.connect(self.on_value_changed)
        self.change_time_spin.valueChanged.connect(self.on_value_changed)
        self.cooldown_time_spin.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self):
        """当任何值改变时调用"""
        self._is_modified = True
        self.save_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.update_window_title()

    def update_window_title(self):
        """更新窗口标题显示修改状态"""
        if self._is_modified:
            self.setWindowTitle("VCGCA-Lite 设置 *")
        else:
            self.setWindowTitle("VCGCA-Lite 设置")

    def load_settings(self):
        """从配置文件加载设置到UI"""
        # 常规设置
        general = settings_manager.get_section("general")
        self.auto_start_cb.setChecked(general.get("auto_start", False))
        self.show_splash_cb.setChecked(general.get("show_splash", True))
        self.copy_to_clipboard_cb.setChecked(general.get("copy_to_clipboard", False))
        self.screenshot_path_edit.setText(general.get("screenshot_path", ""))
        self.show_open_folder_cb.setChecked(general.get("show_open_folder", True))

        # 显示设置
        display = settings_manager.get_section("display")
        self.opacity_spin.setValue(display.get("opacity", 80))
        self.width_spin.setValue(display.get("width", 300))
        self.height_spin.setValue(display.get("height", 150))

        # 位置设置（使用新的滑动条）
        h_pos = display.get("h_position", 100)  # 默认右侧
        v_pos = display.get("v_position", 0)    # 默认顶部
        self.h_pos_slider.setValue(h_pos)
        self.v_pos_slider.setValue(v_pos)
        self.on_h_pos_changed(h_pos)
        self.on_v_pos_changed(v_pos)

        # 手势控制设置
        gesture = settings_manager.get_section("gesture")
        self.prepare_time_spin.setValue(gesture.get("prepare_time", 500))
        self.change_time_spin.setValue(gesture.get("change_time", 1000))
        self.cooldown_time_spin.setValue(gesture.get("cooldown_time", 2000))

        # 加载手势映射
        self._load_gesture_mappings_from_settings(gesture.get("mappings", []))

        # 保存原始值
        self._save_original_values()

        # 重置修改状态
        self._is_modified = False
        self.save_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        self.update_window_title()

    def _save_original_values(self):
        """保存当前UI值为原始值"""
        self._original_values = {
            "auto_start": self.auto_start_cb.isChecked(),
            "show_splash": self.show_splash_cb.isChecked(),
            "copy_to_clipboard": self.copy_to_clipboard_cb.isChecked(),
            "screenshot_path": self.screenshot_path_edit.text(),
            "show_open_folder": self.show_open_folder_cb.isChecked(),
            "opacity": self.opacity_spin.value(),
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "h_position": self.h_pos_slider.value(),
            "v_position": self.v_pos_slider.value(),
            "prepare_time": self.prepare_time_spin.value(),
            "change_time": self.change_time_spin.value(),
            "cooldown_time": self.cooldown_time_spin.value(),
            "gesture_mappings": self._get_gesture_mappings_from_table()
        }

    def save_settings(self):
        """保存UI设置到配置文件"""
        # 常规设置
        settings_manager.set("general", "auto_start", self.auto_start_cb.isChecked())
        settings_manager.set("general", "show_splash", self.show_splash_cb.isChecked())
        settings_manager.set("general", "copy_to_clipboard", self.copy_to_clipboard_cb.isChecked())
        settings_manager.set("general", "screenshot_path", self.screenshot_path_edit.text())
        settings_manager.set("general", "show_open_folder", self.show_open_folder_cb.isChecked())

        # 显示设置
        settings_manager.set("display", "opacity", self.opacity_spin.value())
        settings_manager.set("display", "width", self.width_spin.value())
        settings_manager.set("display", "height", self.height_spin.value())
        settings_manager.set("display", "h_position", self.h_pos_slider.value())
        settings_manager.set("display", "v_position", self.v_pos_slider.value())

        # 手势控制设置
        settings_manager.set("gesture", "prepare_time", self.prepare_time_spin.value())
        settings_manager.set("gesture", "change_time", self.change_time_spin.value())
        settings_manager.set("gesture", "cooldown_time", self.cooldown_time_spin.value())
        settings_manager.set("gesture", "mappings", self._get_gesture_mappings_from_table())

        # 保存到文件
        if settings_manager.save_settings():
            print("设置已保存")
            # 更新原始值和状态
            self._save_original_values()
            self._is_modified = False
            self.save_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.update_window_title()
        else:
            print("设置保存失败")

    def reset_settings(self):
        """重置为原始值（上次保存的值）"""
        if not self._is_modified:
            return

        # 恢复原始值
        self.auto_start_cb.setChecked(self._original_values.get("auto_start", False))
        self.show_splash_cb.setChecked(self._original_values.get("show_splash", True))
        self.copy_to_clipboard_cb.setChecked(self._original_values.get("copy_to_clipboard", False))
        self.screenshot_path_edit.setText(self._original_values.get("screenshot_path", ""))
        self.show_open_folder_cb.setChecked(self._original_values.get("show_open_folder", True))
        self.opacity_spin.setValue(self._original_values.get("opacity", 80))
        self.width_spin.setValue(self._original_values.get("width", 300))
        self.height_spin.setValue(self._original_values.get("height", 150))

        h_pos = self._original_values.get("h_position", 100)
        v_pos = self._original_values.get("v_position", 0)
        self.h_pos_slider.setValue(h_pos)
        self.v_pos_slider.setValue(v_pos)
        self.on_h_pos_changed(h_pos)
        self.on_v_pos_changed(v_pos)

        self.prepare_time_spin.setValue(self._original_values.get("prepare_time", 500))
        self.change_time_spin.setValue(self._original_values.get("change_time", 1000))
        self.cooldown_time_spin.setValue(self._original_values.get("cooldown_time", 2000))
        self._load_gesture_mappings_from_settings(self._original_values.get("gesture_mappings", []))

        # 重置状态
        self._is_modified = False
        self.save_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        self.update_window_title()

    def restore_defaults(self):
        """恢复为程序默认设置"""
        # 默认设置值
        default_values = {
            "auto_start": False,
            "show_splash": True,
            "opacity": 80,
            "width": 300,
            "height": 150,
            "h_position": 100,  # 右侧
            "v_position": 0,    # 顶部
            "prepare_time": 500,
            "change_time": 1000,
            "cooldown_time": 2000
        }

        # 应用默认设置到UI
        self.auto_start_cb.setChecked(default_values["auto_start"])
        self.show_splash_cb.setChecked(default_values["show_splash"])
        self.opacity_spin.setValue(default_values["opacity"])
        self.width_spin.setValue(default_values["width"])
        self.height_spin.setValue(default_values["height"])

        self.h_pos_slider.setValue(default_values["h_position"])
        self.v_pos_slider.setValue(default_values["v_position"])
        self.on_h_pos_changed(default_values["h_position"])
        self.on_v_pos_changed(default_values["v_position"])

        self.prepare_time_spin.setValue(default_values["prepare_time"])
        self.change_time_spin.setValue(default_values["change_time"])
        self.cooldown_time_spin.setValue(default_values["cooldown_time"])
        self._load_gesture_mappings()

        # 标记为已修改，需要保存
        self._is_modified = True
        self.save_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.update_window_title()

        print("已恢复默认设置，请点击保存按钮应用")

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
