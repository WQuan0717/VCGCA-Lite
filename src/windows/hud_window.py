from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QColor, QFont, QMouseEvent

from src.utils.settings_manager import settings_manager
from src.core.gesture_controller import gesture_controller


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
        
        # 记录最后执行的动作
        self.last_action_name = ""
        
        # HUD 功能启用状态（从设置加载，默认启用）
        self.enabled = settings_manager.get("display", "hud_enabled", True)
        
        self.init_ui()
        self.setup_animation()
        self.apply_settings()
        
        # 连接手势控制器信号
        gesture_controller.state_changed.connect(self.on_state_changed)
        gesture_controller.action_triggered.connect(self.on_action_triggered)
        gesture_controller.screenshot_start.connect(self.on_screenshot_start)
        gesture_controller.screenshot_end.connect(self.on_screenshot_end)

        # 截图相关状态
        self.screenshot_in_progress = False
        self.screenshot_success = False
        self.screenshot_message = ""
        
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
        title_label = QLabel("VCGCA-Lite")
        title_font = QFont("Microsoft YaHei", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #3498db;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 主显示内容（根据状态变化）
        self.main_label = QLabel("")
        self.main_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.main_label.setStyleSheet("color: #2ecc71;")  # 默认绿色
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.main_label)
        
        # 副标题/状态信息
        self.sub_label = QLabel("等待手势...")
        self.sub_label.setFont(QFont("Microsoft YaHei", 10))
        self.sub_label.setStyleSheet("color: #95a5a6;")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)
        
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
        
        # 初始隐藏（等待手势服务启动）
        self.hide()
        
    def setup_animation(self):
        # 状态检查定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_state)
        self.timer.start(100)  # 每100ms检查一次状态
        
    def set_enabled(self, enabled):
        """设置 HUD 功能启用状态"""
        self.enabled = enabled
        if not enabled and self.isVisible():
            self.hide()
        
    def check_state(self):
        """检查当前状态，决定是否显示HUD"""
        # 如果正在截图，不显示 HUD（避免被截入画面）
        if self.screenshot_in_progress:
            return

        # 如果 HUD 功能被禁用，不显示
        if not self.enabled:
            if self.isVisible():
                self.hide()
            return

        current_state = gesture_controller.current_state

        # 只在特定状态显示HUD
        if current_state == gesture_controller.STATE_WAITING_RESPONSE:
            # 变化等待期 - 显示"就绪"
            if not self.isVisible():
                self.show()
            self.update_display("就绪", "可以做出响应手势", "#2ecc71")
        elif current_state == gesture_controller.STATE_COOLDOWN:
            # 冷静期 - 显示最后执行的动作
            if not self.isVisible():
                self.show()
            action_text = self.last_action_name if self.last_action_name else "完成"
            self.update_display(action_text, "动作已执行", "#f39c12")
        else:
            # 其他状态 - 隐藏HUD
            if self.isVisible():
                self.hide()
        
    def update_display(self, main_text, sub_text, color):
        """更新显示内容"""
        self.main_label.setText(main_text)
        self.main_label.setStyleSheet(f"color: {color};")
        self.sub_label.setText(sub_text)
        
    def on_state_changed(self, state):
        """状态变化回调"""
        pass  # 在check_state中统一处理
        
    def on_action_triggered(self, prepare, response):
        """动作触发回调 - 记录动作名称"""
        # 获取动作名称
        action_key = gesture_controller._get_action_for_gestures(prepare, response)
        if action_key:
            # 获取动作的中文名称
            action_names = {
                "screenshot": "截图",
                "volume_up": "音量+",
                "volume_down": "音量-",
                "volume_mute": "静音",
                "show_desktop": "桌面",
            }
            self.last_action_name = action_names.get(action_key, action_key)
        else:
            self.last_action_name = "未知动作"

    def on_screenshot_start(self):
        """截图开始 - 立即隐藏 HUD"""
        self.screenshot_in_progress = True
        if self.isVisible():
            self.hide()

    def on_screenshot_end(self, success, message):
        """截图结束 - 显示截图结果"""
        self.screenshot_in_progress = False
        self.screenshot_success = success
        self.screenshot_message = message

        # 统一显示"截图"，与其他动作保持一致
        if self.enabled and success:
            # 截图成功，显示白色闪光效果
            self.show_flash_effect()
            # 记录动作名称为"截图"，冷静期会显示
            self.last_action_name = "截图"

    def show_flash_effect(self):
        """显示全屏白色闪光效果（类似手机截图）"""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer, Qt

        # 创建全屏闪光窗口
        self.flash_widget = QWidget()
        self.flash_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        # 不设置 WA_TranslucentBackground，让白色背景正常显示
        self.flash_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 设置全屏
        screen = QApplication.primaryScreen().geometry()
        self.flash_widget.setGeometry(screen)

        # 设置白色背景（使用 palette 确保生效）
        from PyQt6.QtGui import QPalette
        palette = self.flash_widget.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        self.flash_widget.setPalette(palette)
        self.flash_widget.setAutoFillBackground(True)

        # 显示闪光窗口
        self.flash_widget.show()
        self.flash_widget.raise_()

        # 150ms 后开始淡出（让白色显示更久一些）
        QTimer.singleShot(150, self._fade_flash)

    def _fade_flash(self):
        """淡出闪光效果"""
        if hasattr(self, 'flash_widget') and self.flash_widget:
            # 使用 QTimer 逐步降低透明度（更简单可靠）
            self.flash_opacity = 1.0
            self.flash_timer = QTimer(self)
            self.flash_timer.timeout.connect(self._update_flash_opacity)
            self.flash_timer.start(20)  # 每 20ms 更新一次

    def _update_flash_opacity(self):
        """更新闪光透明度"""
        self.flash_opacity -= 0.05  # 每次降低 5%
        if self.flash_opacity <= 0:
            self.flash_timer.stop()
            self._cleanup_flash()
        else:
            # 使用窗口透明度
            self.flash_widget.setWindowOpacity(self.flash_opacity)

    def _cleanup_flash(self):
        """清理闪光窗口"""
        if hasattr(self, 'flash_widget') and self.flash_widget:
            self.flash_widget.close()
            self.flash_widget = None

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
