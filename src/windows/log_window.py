"""
日志查看器窗口
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QComboBox, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QSplitter, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QTextCharFormat, QFont

from src.utils.logger import log_manager


class LogWindow(QMainWindow):
    """日志查看器窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("日志查看器 - VCGCA-Lite")
        self.setMinimumSize(900, 600)

        self.init_ui()
        self.connect_signals()
        self.refresh_log_files()

    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # 左侧：日志文件列表
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 日志文件列表
        file_group = QGroupBox("日志文件")
        file_layout = QVBoxLayout(file_group)

        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["文件名", "大小", "修改时间"])
        self.file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.file_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.file_table.itemClicked.connect(self.on_file_selected)
        file_layout.addWidget(self.file_table)

        # 刷新按钮
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self.refresh_log_files)
        file_layout.addWidget(refresh_btn)

        # 清理旧日志按钮
        clear_btn = QPushButton("清理7天前日志")
        clear_btn.clicked.connect(self.clear_old_logs)
        file_layout.addWidget(clear_btn)

        left_layout.addWidget(file_group)

        # 右侧：日志内容
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 工具栏
        toolbar = QHBoxLayout()

        # 日志级别过滤
        toolbar.addWidget(QLabel("日志级别:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.apply_filter)
        toolbar.addWidget(self.level_combo)

        # 自动刷新
        self.auto_refresh_btn = QPushButton("自动刷新: 关")
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        toolbar.addWidget(self.auto_refresh_btn)

        # 清空显示
        clear_display_btn = QPushButton("清空显示")
        clear_display_btn.clicked.connect(self.clear_display)
        toolbar.addWidget(clear_display_btn)

        toolbar.addStretch()
        right_layout.addLayout(toolbar)

        # 日志内容显示
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.log_display)

        # 实时日志
        realtime_group = QGroupBox("实时日志")
        realtime_layout = QVBoxLayout(realtime_group)

        self.realtime_display = QTextEdit()
        self.realtime_display.setReadOnly(True)
        self.realtime_display.setMaximumHeight(150)
        self.realtime_display.setFont(QFont("Consolas", 9))
        realtime_layout.addWidget(self.realtime_display)

        right_layout.addWidget(realtime_group)

        # 添加到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])

        # 自动刷新定时器
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_current_log)

    def connect_signals(self):
        """连接信号"""
        log_manager.new_log_message.connect(self.on_new_log)

    def refresh_log_files(self):
        """刷新日志文件列表"""
        files = log_manager.get_log_files()

        self.file_table.setRowCount(len(files))
        for i, file_info in enumerate(files):
            self.file_table.setItem(i, 0, QTableWidgetItem(file_info['name']))
            size_mb = file_info['size'] / 1024 / 1024
            self.file_table.setItem(i, 1, QTableWidgetItem(f"{size_mb:.2f} MB"))
            self.file_table.setItem(i, 2, QTableWidgetItem(file_info['modified']))

        self.file_table.resizeColumnsToContents()

    def on_file_selected(self, item):
        """选择日志文件"""
        row = item.row()
        file_name = self.file_table.item(row, 0).text()
        log_path = log_manager.log_dir / file_name

        self.current_log_path = str(log_path)
        self.load_log_content()

    def load_log_content(self):
        """加载日志内容"""
        if hasattr(self, 'current_log_path'):
            content = log_manager.read_log_file(self.current_log_path, lines=500)
            self.apply_filter_to_content(content)

    def apply_filter_to_content(self, content):
        """应用过滤器到内容"""
        level = self.level_combo.currentText()

        if level == "ALL":
            self.log_display.setPlainText(content)
        else:
            filtered_lines = []
            for line in content.split('\n'):
                if f'[{level}]' in line:
                    filtered_lines.append(line)
            self.log_display.setPlainText('\n'.join(filtered_lines))

        # 滚动到底部
        self.log_display.moveCursor(self.log_display.textCursor().MoveOperation.End)

    def apply_filter(self):
        """应用过滤器"""
        self.load_log_content()

    def refresh_current_log(self):
        """刷新当前日志"""
        self.load_log_content()

    def toggle_auto_refresh(self, checked):
        """切换自动刷新"""
        if checked:
            self.auto_refresh_btn.setText("自动刷新: 开")
            self.refresh_timer.start(2000)  # 每2秒刷新
        else:
            self.auto_refresh_btn.setText("自动刷新: 关")
            self.refresh_timer.stop()

    def clear_display(self):
        """清空显示"""
        self.log_display.clear()

    def clear_old_logs(self):
        """清理旧日志"""
        count = log_manager.clear_old_logs(days=7)
        self.refresh_log_files()
        log_manager.info(f"通过日志查看器清理了 {count} 个旧日志文件")

    def on_new_log(self, level, message):
        """新日志消息"""
        # 添加到实时显示
        self.realtime_display.append(message)

        # 限制行数
        if self.realtime_display.document().blockCount() > 100:
            cursor = self.realtime_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()

        # 根据级别设置颜色
        color_map = {
            'DEBUG': QColor(128, 128, 128),
            'INFO': QColor(0, 0, 0),
            'WARNING': QColor(255, 165, 0),
            'ERROR': QColor(255, 0, 0),
            'CRITICAL': QColor(139, 0, 0)
        }

        if level in color_map:
            cursor = self.realtime_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            format = QTextCharFormat()
            format.setForeground(color_map[level])
            cursor.mergeCharFormat(format)

    def closeEvent(self, event):
        """关闭事件"""
        self.refresh_timer.stop()
        event.accept()
