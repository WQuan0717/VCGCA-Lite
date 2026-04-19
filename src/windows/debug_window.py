import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextEdit
from PyQt6.QtGui import QImage, QPixmap, QIcon


class DebugWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.frame_count = 0
        
    def run(self):
        while self.running:
            # 创建一个测试图像（模拟OpenCV处理）
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # 绘制背景渐变
            for i in range(480):
                color = int(255 * (i / 480))
                frame[i, :] = [color // 3, color // 2, color]
            
            # 绘制一些图形
            cv2.circle(frame, (320, 240), 100, (0, 255, 0), 2)
            cv2.rectangle(frame, (200, 160), (440, 320), (255, 0, 0), 2)
            cv2.line(frame, (0, 0), (640, 480), (0, 0, 255), 2)
            
            # 添加文字
            self.frame_count += 1
            text = f"Frame: {self.frame_count}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (255, 255, 255), 2)
            cv2.putText(frame, "Debug Mode - OpenCV", (10, 460), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            self.frame_ready.emit(frame)
            
            if self.frame_count % 30 == 0:
                self.log_message.emit(f"Processed frame {self.frame_count}")
            
            # 控制帧率约30fps
            self.msleep(33)
            
    def stop(self):
        self.running = False
        self.wait()


class DebugWindow(QWidget):
    closed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCGCA-Lite 调试窗口")
        self.setMinimumSize(700, 600)
        self.setWindowIcon(QIcon())
        
        self.worker = None
        self.init_ui()
        self.start_debug_worker()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 视频显示区域
        self.video_label = QLabel("初始化中...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: #1a1a1a; color: #fff;")
        layout.addWidget(self.video_label)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始")
        self.start_btn.clicked.connect(self.start_debug_worker)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_debug_worker)
        
        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.clicked.connect(self.clear_log)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
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
        
    def start_debug_worker(self):
        if self.worker is None or not self.worker.isRunning():
            self.worker = DebugWorker()
            self.worker.frame_ready.connect(self.update_frame)
            self.worker.log_message.connect(self.add_log)
            self.worker.start()
            self.add_log("调试工作线程已启动")
            
    def stop_debug_worker(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.add_log("调试工作线程已停止")
            
    def update_frame(self, frame):
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
        self.stop_debug_worker()
        self.closed.emit()
        event.accept()
