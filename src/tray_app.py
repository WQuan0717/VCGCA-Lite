import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QThread

from src.windows.settings_window import SettingsWindow
from src.windows.hud_window import HUDWindow
from src.windows.debug_window import DebugWindow
from src.windows.splash_window import SplashWindow
from src.windows.log_window import LogWindow
from src.windows.help_window import HelpWindow
from src.utils.icon_helper import create_default_icon
from src.utils.settings_manager import settings_manager
from src.utils.startup_manager import StartupManager
from src.utils.logger import log_manager
from src.utils.error_handler import error_handler
from src.core.gesture_service import gesture_service


class TrayApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 安装全局错误处理器
        error_handler.install_global_handler()

        # 窗口实例（单例模式）
        self.settings_window = None
        self.hud_window = None
        self.debug_window = None
        self.splash_window = None
        self.log_window = None
        self.help_window = None

        # HUD 功能启用状态（从设置加载，默认启用）
        self.hud_enabled = settings_manager.get("display", "hud_enabled", True)

        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(create_default_icon())
        self.tray_icon.setToolTip("VCGCA-Lite")

        # 创建托盘菜单
        self.create_tray_menu()

        # 托盘图标双击事件
        self.tray_icon.activated.connect(self.on_tray_activated)

        # 连接设置变更信号
        settings_manager.settings_changed.connect(self.on_settings_changed)

    def create_tray_menu(self):
        menu = QMenu()

        # 显示设置
        settings_action = QAction("显示设置", self.app)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)

        # HUD 功能启用/禁用
        self.hud_action = QAction("", self.app)
        self.hud_action.triggered.connect(self.toggle_hud_enabled)
        self.update_hud_menu_text()
        menu.addAction(self.hud_action)

        # 显示调试窗口
        debug_action = QAction("显示调试窗口", self.app)
        debug_action.triggered.connect(self.show_debug_window)
        menu.addAction(debug_action)

        # 显示日志查看器
        log_action = QAction("查看日志", self.app)
        log_action.triggered.connect(self.show_log_window)
        menu.addAction(log_action)

        # 帮助文档
        help_action = QAction("帮助文档", self.app)
        help_action.triggered.connect(self.show_help_window)
        menu.addAction(help_action)

        menu.addSeparator()

        # 退出
        exit_action = QAction("退出", self.app)
        exit_action.triggered.connect(self.quit)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)

    def on_tray_activated(self, reason):
        # 双击托盘图标显示设置窗口
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings()

    def show_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
            self.settings_window.closed.connect(self.on_settings_closed)
            self.settings_window.show()
        else:
            self.settings_window.raise_()
            self.settings_window.activateWindow()

    def on_settings_closed(self):
        self.settings_window = None

    def toggle_hud_enabled(self):
        """切换 HUD 功能的启用/禁用状态"""
        self.hud_enabled = not self.hud_enabled

        # 保存到设置
        settings_manager.set("display", "hud_enabled", self.hud_enabled)
        settings_manager.save_settings()

        # 更新菜单文本
        self.update_hud_menu_text()

        if self.hud_enabled:
            # 启用 HUD，创建窗口（如果不存在）
            self.create_hud_window()
        else:
            # 禁用 HUD，隐藏窗口
            if self.hud_window and self.hud_window.isVisible():
                self.hud_window.hide()

        # 通知 HUD 窗口状态变化
        if self.hud_window:
            self.hud_window.set_enabled(self.hud_enabled)

    def update_hud_menu_text(self):
        """更新 HUD 菜单项的文本"""
        if self.hud_enabled:
            self.hud_action.setText("禁用HUD提示")
        else:
            self.hud_action.setText("启用HUD提示")

    def sync_startup_status(self):
        """同步开机启动状态（确保注册表和设置文件一致）"""
        try:
            # 获取设置中的开机启动状态
            settings_auto_start = settings_manager.get("general", "auto_start", False)

            # 获取实际注册表中的状态
            registry_auto_start = StartupManager.is_auto_start_enabled()

            # 如果不一致，以设置文件为准
            if settings_auto_start != registry_auto_start:
                log_manager.info(f"同步开机启动状态: 设置={settings_auto_start}, 注册表={registry_auto_start}")
                StartupManager.toggle_auto_start(settings_auto_start)
        except Exception as e:
            log_manager.error(f"同步开机启动状态失败: {e}")

    def show_debug_window(self):
        if self.debug_window is None:
            self.debug_window = DebugWindow()
            self.debug_window.closed.connect(self.on_debug_closed)
            self.debug_window.show()
        else:
            self.debug_window.raise_()
            self.debug_window.activateWindow()

    def on_debug_closed(self):
        self.debug_window = None

    def show_log_window(self):
        """显示日志查看器"""
        if self.log_window is None:
            self.log_window = LogWindow()
            self.log_window.closed.connect(self.on_log_window_closed)
            self.log_window.show()
        else:
            self.log_window.raise_()
            self.log_window.activateWindow()

    def on_log_window_closed(self):
        """日志窗口关闭"""
        self.log_window = None

    def show_help_window(self):
        """显示帮助文档窗口"""
        if self.help_window is None:
            self.help_window = HelpWindow()
            self.help_window.closed.connect(self.on_help_window_closed)
            self.help_window.show()
        else:
            self.help_window.raise_()
            self.help_window.activateWindow()

    def on_help_window_closed(self):
        """帮助窗口关闭"""
        self.help_window = None

    def on_settings_changed(self, section, key, value):
        """设置变更时立即应用"""
        log_manager.info(f"设置变更: {section}.{key} = {value}")

        # 同步 HUD 启用状态
        if section == "display" and key == "hud_enabled":
            self.hud_enabled = value
            self.update_hud_menu_text()
            if self.hud_window:
                self.hud_window.set_enabled(self.hud_enabled)

        # 处理开机启动设置变更
        if section == "general" and key == "auto_start":
            success = StartupManager.toggle_auto_start(value)
            if success:
                log_manager.info(f"开机启动已{'启用' if value else '禁用'}")
            else:
                log_manager.error(f"开机启动设置失败")

    def quit(self):
        # 停止手势识别服务
        if gesture_service.isRunning():
            gesture_service.stop()
            log_manager.info("手势识别服务已停止")
        # 清理所有窗口
        if self.settings_window:
            self.settings_window.close()
        if self.hud_window:
            self.hud_window.close()
        if self.debug_window:
            self.debug_window.close()
        if hasattr(self, 'log_window') and self.log_window:
            self.log_window.close()
        if hasattr(self, 'help_window') and self.help_window:
            self.help_window.close()
        self.tray_icon.hide()
        self.app.quit()

    def show_splash_and_run(self):
        """显示启动动画后开始运行"""
        # 同步开机启动状态（确保注册表和设置文件一致）
        self.sync_startup_status()

        # 检查是否显示启动动画
        show_splash = settings_manager.get("general", "show_splash", True)

        if show_splash:
            # 创建并显示启动动画
            self.splash_window = SplashWindow()
            self.splash_window.finished.connect(self.on_splash_finished)
            self.splash_window.start()
        else:
            # 直接显示托盘图标并启动手势识别
            self.tray_icon.show()
            self.start_gesture_service()

    def on_splash_finished(self):
        """启动动画完成后"""
        self.splash_window = None
        self.tray_icon.show()
        # 自动启动手势识别服务
        self.start_gesture_service()

    def start_gesture_service(self):
        """启动手势识别服务"""
        if not gesture_service.isRunning():
            # 连接日志信号到控制台输出
            gesture_service.log_message.connect(self.on_gesture_log)
            gesture_service.gesture_detected.connect(self.on_gesture_detected)
            # 初始化并启动
            if gesture_service.initialize():
                gesture_service.start()
                log_manager.info("手势识别服务已自动启动")
                # 创建 HUD 窗口（如果启用了 HUD）
                if self.hud_enabled:
                    self.create_hud_window()
            else:
                log_manager.error("手势识别服务启动失败")

    def create_hud_window(self):
        """创建 HUD 窗口"""
        if self.hud_window is None:
            self.hud_window = HUDWindow()
            self.hud_window.set_enabled(self.hud_enabled)

    def on_gesture_log(self, message):
        """接收手势识别日志"""
        log_manager.info(f"[Gesture] {message}")

    def on_gesture_detected(self, gesture_name, confidence):
        """处理检测到的手势"""
        # 这里可以添加手势对应的操作
        pass

    def run(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            log_manager.critical("系统不支持托盘图标")
            sys.exit(1)

        # 显示启动动画（如果启用）
        self.show_splash_and_run()

        sys.exit(self.app.exec())
