from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QColor, QFont, QMouseEvent

from src.utils.settings_manager import settings_manager


class HUDWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCGCA-Lite HUD")
        self.setMinimumSize(300, 150)
        self.setMaximumSize(400, 200)
        
        # 无边框、置顶、工具窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        
        # 透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 拖动相关
        self.dragging = False
        self.drag_position = QPoint()
        
        self.init_ui()
        self.setup_animation()
        self.apply_settings()
        
    def init_ui(self):
        # 主布局
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 15px;
                border: 2px solid rgba(52, 152, 219, 180);
            }
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("VCGCA-Lite HUD")
        title_font = QFont("Microsoft YaHei", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #3498db;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 状态信息
        self.status_label = QLabel("系统运行中...")
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        self.status_label.setStyleSheet("color: #ecf0f1;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 数据展示
        self.data_label = QLabel("FPS: 60 | 延迟: 16ms")
        self.data_label.setFont(QFont("Microsoft YaHei", 9))
        self.data_label.setStyleSheet("color: #95a5a6;")
        self.data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.data_label)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        # 设置容器大小
        self.container.setGeometry(10, 10, 280, 130)
        self.setFixedSize(300, 150)
        
        # 默认位置：屏幕右上角
        screen = self.screen().geometry()
        self.move(screen.width() - 320, 50)
        
    def setup_animation(self):
        # 模拟数据更新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # 每秒更新
        
        self.frame_count = 0
        
    def update_data(self):
        self.frame_count += 1
        import random
        fps = random.randint(58, 62)
        latency = random.randint(14, 18)
        self.data_label.setText(f"FPS: {fps} | 延迟: {latency}ms")
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
            
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        # 双击隐藏
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide()
            event.accept()
    
    def apply_settings(self):
        """应用设置到HUD窗口"""
        # 获取显示设置
        opacity = settings_manager.get("display", "opacity", 80)
        width = settings_manager.get("display", "width", 300)
        height = settings_manager.get("display", "height", 150)
        h_position = settings_manager.get("display", "h_position", 100)  # 0-100
        v_position = settings_manager.get("display", "v_position", 0)    # 0-100

        # 应用透明度
        opacity_value = int(255 * (opacity / 100))
        self.container.setStyleSheet(f"""
            #container {{
                background-color: rgba(30, 30, 30, {opacity_value});
                border-radius: 15px;
                border: 2px solid rgba(52, 152, 219, 180);
            }}
        """)

        # 应用尺寸
        container_width = width - 20  # 减去边距
        container_height = height - 20
        self.container.setGeometry(10, 10, container_width, container_height)
        self.setFixedSize(width, height)

        # 应用位置（使用百分比计算）
        screen = self.screen().geometry()

        # 水平位置：0% = 最左，50% = 居中，100% = 最右
        if h_position == 50:
            x = (screen.width() - width) // 2
        else:
            x = int((screen.width() - width) * h_position / 100)

        # 垂直位置：0% = 最上，50% = 居中，100% = 最下
        if v_position == 50:
            y = (screen.height() - height) // 2
        else:
            y = int((screen.height() - height) * v_position / 100)

        self.move(x, y)
