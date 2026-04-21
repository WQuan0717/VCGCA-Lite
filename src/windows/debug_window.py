import cv2
import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextEdit
from PyQt6.QtGui import QImage, QPixmap, QIcon

from src.core.gesture_service import gesture_service


class DebugWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCGCA-Lite 调试窗口 - 视频预览")
        self.setMinimumSize(700, 650)
        self.setWindowIcon(QIcon())

        self.init_ui()
        self.connect_to_service()

        # 创建定时器检查服务状态
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_button_states)
        self.status_timer.start(500)  # 每500ms检查一次

    def init_ui(self):
        layout = QVBoxLayout()

        # 视频显示区域
        self.video_label = QLabel("等待手势识别服务...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: #1a1a1a; color: #fff;")
        layout.addWidget(self.video_label)

        # 控制按钮
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始服务")
        self.start_btn.clicked.connect(self.start_service)
        self.start_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)

        self.stop_btn = QPushButton("停止服务")
        self.stop_btn.clicked.connect(self.stop_service)
        self.stop_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)

        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.clicked.connect(self.clear_log)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        # 日志区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: Consolas, monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

        # 初始化按钮状态
        self.update_button_states()

    def update_button_states(self):
        """根据服务状态更新按钮可用性"""
        is_running = gesture_service.isRunning()
        self.start_btn.setEnabled(not is_running)
        self.stop_btn.setEnabled(is_running)

        # 更新视频标签状态
        if is_running:
            if self.video_label.text() in ["等待手势识别服务...", "手势识别服务未运行"]:
                self.video_label.setText("手势识别服务运行中")
        else:
            if self.video_label.pixmap() is not None:
                self.video_label.clear()
            self.video_label.setText("手势识别服务未运行")

    def connect_to_service(self):
        """连接到手势识别服务"""
        # 连接信号
        gesture_service.log_message.connect(self.add_log)
        gesture_service.frame_ready.connect(self.update_frame)

        # 检查服务是否已启动
        if gesture_service.isRunning():
            self.add_log("已连接到手势识别服务")
            gesture_service.connect_preview()
        else:
            self.add_log("手势识别服务尚未启动，点击'开始服务'启动")

    def start_service(self):
        """开始手势识别服务"""
        if not gesture_service.isRunning():
            self.add_log("正在启动手势识别服务...")
            if gesture_service.initialize():
                gesture_service.start()
                gesture_service.connect_preview()
                self.add_log("手势识别服务已启动")
            else:
                self.add_log("手势识别服务启动失败")
            self.update_button_states()

    def stop_service(self):
        """停止手势识别服务"""
        if gesture_service.isRunning():
            gesture_service.disconnect_preview()
            gesture_service.stop()
            self.add_log("手势识别服务已停止")
            self.video_label.clear()
            self.video_label.setText("手势识别服务已停止")
            self.update_button_states()

    def update_frame(self, frame):
        """更新视频帧"""
        # 将OpenCV图像转换为QPixmap
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    def add_log(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def clear_log(self):
        self.log_text.clear()

    def closeEvent(self, event):
        # 断开预览，但不停止手势识别服务
        gesture_service.disconnect_preview()
        gesture_service.log_message.disconnect(self.add_log)
        gesture_service.frame_ready.disconnect(self.update_frame)
        self.status_timer.stop()
        self.closed.emit()
        event.accept()
