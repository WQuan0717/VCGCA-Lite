from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QCheckBox, QGroupBox,
                             QSpinBox, QComboBox, QTabWidget, QSlider, QGridLayout,
                             QTextBrowser)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from src.utils.settings_manager import settings_manager
from src.utils.version import get_version_string, get_full_version_info, APP_NAME, APP_DESCRIPTION


class SettingsWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCGCA-Lite 设置")
        self.setMinimumSize(500, 400)
        self.setWindowIcon(QIcon())  # 可以设置一个图标

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
        tabs.addTab(self.create_advanced_tab(), "高级")
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

    def create_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # 调试设置
        debug_group = QGroupBox("调试设置")
        debug_layout = QVBoxLayout()

        self.debug_mode_cb = QCheckBox("启用调试模式")
        self.log_to_file_cb = QCheckBox("记录日志到文件")

        debug_layout.addWidget(self.debug_mode_cb)
        debug_layout.addWidget(self.log_to_file_cb)
        debug_group.setLayout(debug_layout)

        layout.addWidget(debug_group)
        layout.addStretch()

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

        # 显示设置
        self.opacity_spin.valueChanged.connect(self.on_value_changed)
        self.width_spin.valueChanged.connect(self.on_value_changed)
        self.height_spin.valueChanged.connect(self.on_value_changed)

        # 高级设置
        self.debug_mode_cb.stateChanged.connect(self.on_value_changed)
        self.log_to_file_cb.stateChanged.connect(self.on_value_changed)

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

        # 高级设置
        advanced = settings_manager.get_section("advanced")
        self.debug_mode_cb.setChecked(advanced.get("debug_mode", False))
        self.log_to_file_cb.setChecked(advanced.get("log_to_file", False))

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
            "opacity": self.opacity_spin.value(),
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "h_position": self.h_pos_slider.value(),
            "v_position": self.v_pos_slider.value(),
            "debug_mode": self.debug_mode_cb.isChecked(),
            "log_to_file": self.log_to_file_cb.isChecked()
        }

    def save_settings(self):
        """保存UI设置到配置文件"""
        # 常规设置
        settings_manager.set("general", "auto_start", self.auto_start_cb.isChecked())
        settings_manager.set("general", "show_splash", self.show_splash_cb.isChecked())

        # 显示设置
        settings_manager.set("display", "opacity", self.opacity_spin.value())
        settings_manager.set("display", "width", self.width_spin.value())
        settings_manager.set("display", "height", self.height_spin.value())
        settings_manager.set("display", "h_position", self.h_pos_slider.value())
        settings_manager.set("display", "v_position", self.v_pos_slider.value())

        # 高级设置
        settings_manager.set("advanced", "debug_mode", self.debug_mode_cb.isChecked())
        settings_manager.set("advanced", "log_to_file", self.log_to_file_cb.isChecked())

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
        self.opacity_spin.setValue(self._original_values.get("opacity", 80))
        self.width_spin.setValue(self._original_values.get("width", 300))
        self.height_spin.setValue(self._original_values.get("height", 150))

        h_pos = self._original_values.get("h_position", 100)
        v_pos = self._original_values.get("v_position", 0)
        self.h_pos_slider.setValue(h_pos)
        self.v_pos_slider.setValue(v_pos)
        self.on_h_pos_changed(h_pos)
        self.on_v_pos_changed(v_pos)

        self.debug_mode_cb.setChecked(self._original_values.get("debug_mode", False))
        self.log_to_file_cb.setChecked(self._original_values.get("log_to_file", False))

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
            "debug_mode": False,
            "log_to_file": False
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

        self.debug_mode_cb.setChecked(default_values["debug_mode"])
        self.log_to_file_cb.setChecked(default_values["log_to_file"])

        # 标记为已修改，需要保存
        self._is_modified = True
        self.save_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.update_window_title()

        print("已恢复默认设置，请点击保存按钮应用")

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
