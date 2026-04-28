"""
简化日志查看器
- 类似终端的界面
- 实时显示日志
- 支持筛选和暂停刷新
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QTextCharFormat, QFont

from src.utils.logger import log_manager
from src.utils.icon_helper import get_application_icon


class LogWindow(QMainWindow):
    """简化日志查看器窗口"""
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("日志查看器 - VCGCA-Lite")
        self.setMinimumSize(800, 500)
        self.setWindowIcon(get_application_icon())

        # 暂停刷新标志
        self.pause_refresh = False
        # 当前筛选级别
        self.filter_level = "ALL"
        # 待显示的日志缓存（暂停时积累）
        self.pending_logs = []

        self.init_ui()
        self.load_logs()

        # 连接信号
        log_manager.new_log_message.connect(self.on_new_log)

    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # 工具栏
        toolbar = QHBoxLayout()

        # 日志文件路径显示
        self.path_label = QLabel(f"日志文件: {log_manager.get_log_file_path()}")
        self.path_label.setStyleSheet("color: #666; font-size: 11px;")
        toolbar.addWidget(self.path_label)

        toolbar.addStretch()

        # 级别筛选
        toolbar.addWidget(QLabel("筛选:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.filter_combo.setCurrentText("ALL")
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        toolbar.addWidget(self.filter_combo)

        # 暂停/继续刷新按钮
        self.pause_btn = QPushButton("暂停刷新")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.on_pause_toggle)
        toolbar.addWidget(self.pause_btn)

        # 清空按钮
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(clear_btn)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        toolbar.addWidget(close_btn)

        layout.addLayout(toolbar)

        # 日志显示区域（类似终端）
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 5px;
            }
        """)
        layout.addWidget(self.log_display)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.status_label)

    def load_logs(self):
        """加载所有日志"""
        logs = log_manager.get_all_logs()
        self.log_display.setPlainText(logs)
        self._colorize_all()
        self._scroll_to_bottom()
        self._update_status()

    def _colorize_all(self):
        """为所有日志添加颜色"""
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)

        text = self.log_display.toPlainText()
        lines = text.split('\n')

        for line in lines:
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)

            fmt = QTextCharFormat()
            if '[CRITICAL]' in line or '[ERROR]' in line:
                fmt.setForeground(QColor('#f48771'))
            elif '[WARNING]' in line:
                fmt.setForeground(QColor('#dcdcaa'))
            elif '[INFO]' in line:
                fmt.setForeground(QColor('#4fc1ff'))
            elif '[DEBUG]' in line:
                fmt.setForeground(QColor('#808080'))
            else:
                fmt.setForeground(QColor('#d4d4d4'))

            cursor.mergeCharFormat(fmt)
            cursor.movePosition(cursor.MoveOperation.NextBlock)

    def _colorize_line(self, line):
        """为单行设置颜色"""
        fmt = QTextCharFormat()
        if '[CRITICAL]' in line or '[ERROR]' in line:
            fmt.setForeground(QColor('#f48771'))
        elif '[WARNING]' in line:
            fmt.setForeground(QColor('#dcdcaa'))
        elif '[INFO]' in line:
            fmt.setForeground(QColor('#4fc1ff'))
        elif '[DEBUG]' in line:
            fmt.setForeground(QColor('#808080'))
        else:
            fmt.setForeground(QColor('#d4d4d4'))
        return fmt

    def _should_show_log(self, level, message):
        """检查是否应该显示该日志"""
        if self.filter_level == "ALL":
            return True
        return f"[{self.filter_level}]" in message

    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _update_status(self):
        """更新状态栏"""
        line_count = self.log_display.document().blockCount()
        status = f"共 {line_count} 行日志 | 最大保留 2000 行"
        if self.pause_refresh:
            status += f" | 已暂停 ({len(self.pending_logs)} 条待显示)"
        self.status_label.setText(status)

    def on_new_log(self, level, message):
        """新日志消息"""
        # 如果暂停刷新，缓存起来
        if self.pause_refresh:
            self.pending_logs.append((level, message))
            self._update_status()
            return

        # 检查是否符合筛选条件
        if not self._should_show_log(level, message):
            return

        # 添加到显示
        self.log_display.append(message)

        # 设置颜色
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
        cursor.mergeCharFormat(self._colorize_line(message))

        # 滚动到底部
        self._scroll_to_bottom()
        self._update_status()

    def on_pause_toggle(self, checked):
        """暂停/继续刷新切换"""
        self.pause_refresh = checked
        if checked:
            self.pause_btn.setText("继续刷新")
            self.pause_btn.setStyleSheet("background-color: #ff9800; color: white;")
        else:
            self.pause_btn.setText("暂停刷新")
            self.pause_btn.setStyleSheet("")
            # 显示缓存的日志
            self._flush_pending_logs()
        self._update_status()

    def _flush_pending_logs(self):
        """刷新缓存的日志"""
        for level, message in self.pending_logs:
            if self._should_show_log(level, message):
                self.log_display.append(message)
                cursor = self.log_display.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
                cursor.mergeCharFormat(self._colorize_line(message))
        self.pending_logs.clear()
        self._scroll_to_bottom()
        self._update_status()

    def on_filter_changed(self, level):
        """筛选级别改变"""
        self.filter_level = level
        # 重新加载所有日志并应用筛选
        self.log_display.clear()
        all_logs = log_manager.get_all_logs().strip().split('\n')
        for line in all_logs:
            if line.strip() and self._should_show_log("", line):
                self.log_display.append(line)
                cursor = self.log_display.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
                cursor.mergeCharFormat(self._colorize_line(line))
        self._scroll_to_bottom()
        self._update_status()

    def clear_logs(self):
        """清空日志"""
        log_manager.clear_logs()
        self.log_display.clear()
        self.pending_logs.clear()
        self._update_status()

    def closeEvent(self, event):
        """关闭事件"""
        try:
            log_manager.new_log_message.disconnect(self.on_new_log)
        except:
            pass
        self.closed.emit()
        event.accept()
