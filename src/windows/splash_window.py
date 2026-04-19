from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QLinearGradient

from src.utils.version import get_version_string


class SplashWindow(QWidget):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCGCA-Lite")
        self.setFixedSize(400, 250)
        
        # 无边框、置顶、工具窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        # 主容器
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 20px;
                border: 2px solid rgba(52, 152, 219, 200);
            }
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)
        
        # 应用名称
        title_label = QLabel("VCGCA-Lite")
        title_font = QFont("Microsoft YaHei", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #3498db;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("系统工具")
        subtitle_font = QFont("Microsoft YaHei", 12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #95a5a6;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(20)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 状态文字
        self.status_label = QLabel("正在启动...")
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        self.status_label.setStyleSheet("color: #ecf0f1;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 版本号（从版本信息文件加载）
        version_text = f"v{get_version_string()}"
        version_label = QLabel(version_text)
        version_label.setFont(QFont("Microsoft YaHei", 9))
        version_label.setStyleSheet("color: #7f8c8d;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)
        
        # 设置容器大小和位置
        self.container.setGeometry(10, 10, 380, 230)
        
        # 窗口居中显示
        screen = self.screen().geometry()
        self.move(
            (screen.width() - 400) // 2,
            (screen.height() - 250) // 2
        )
        
    def setup_animations(self):
        # 进度值
        self.current_progress = 0
        self.target_progress = 0
        
        # 淡入动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(500)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 淡出动画
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(500)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_out_animation.finished.connect(self.on_fade_out_finished)
        
        # 进度更新定时器
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        
        # 状态文字更新
        self.status_messages = [
            (0, "正在初始化..."),
            (20, "正在加载配置..."),
            (40, "正在初始化组件..."),
            (60, "正在准备界面..."),
            (80, "即将完成..."),
            (100, "启动完成")
        ]
        
    def start(self):
        """开始显示启动动画"""
        self.show()
        self.opacity_animation.start()
        self.progress_timer.start(30)  # 每30ms更新一次
        
    def update_progress(self):
        """更新进度"""
        if self.current_progress < 100:
            self.current_progress += 1
            self.progress_bar.setValue(self.current_progress)
            
            # 更新状态文字
            for progress, message in self.status_messages:
                if self.current_progress >= progress:
                    self.status_label.setText(message)
        else:
            # 进度完成，开始淡出
            self.progress_timer.stop()
            QTimer.singleShot(500, self.start_fade_out)
            
    def start_fade_out(self):
        """开始淡出"""
        self.fade_out_animation.start()
        
    def on_fade_out_finished(self):
        """淡出完成"""
        self.hide()
        self.finished.emit()
        
    def skip(self):
        """跳过动画"""
        self.progress_timer.stop()
        self.start_fade_out()
        
    def mousePressEvent(self, event):
        """点击跳过动画"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.skip()
            event.accept()
