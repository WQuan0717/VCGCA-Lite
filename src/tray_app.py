import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QThread

from src.windows.settings_window import SettingsWindow
from src.windows.hud_window import HUDWindow
from src.windows.debug_window import DebugWindow
from src.windows.splash_window import SplashWindow
from src.utils.icon_helper import create_default_icon
from src.utils.settings_manager import settings_manager


class TrayApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 窗口实例（单例模式）
        self.settings_window = None
        self.hud_window = None
        self.debug_window = None
        self.splash_window = None

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
        
        # 显示/隐藏 HUD
        self.hud_action = QAction("显示/隐藏HUD", self.app)
        self.hud_action.triggered.connect(self.toggle_hud)
        menu.addAction(self.hud_action)
        
        # 显示调试窗口
        debug_action = QAction("显示调试窗口", self.app)
        debug_action.triggered.connect(self.show_debug_window)
        menu.addAction(debug_action)
        
        menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self.app)
        exit_action.triggered.connect(self.quit)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        
    def on_tray_activated(self, reason):
        # 双击托盘图标显示/隐藏HUD
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_hud()
            
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
        
    def toggle_hud(self):
        if self.hud_window is None:
            self.hud_window = HUDWindow()
            self.hud_window.show()
        else:
            if self.hud_window.isVisible():
                self.hud_window.hide()
            else:
                self.hud_window.show()
                self.hud_window.raise_()
                
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
        
    def on_settings_changed(self, section, key, value):
        """设置变更时立即应用"""
        print(f"设置变更: {section}.{key} = {value}")
        
        # 如果HUD窗口已打开，立即应用显示相关设置
        if self.hud_window and self.hud_window.isVisible():
            if section == "display":
                self.hud_window.apply_settings()
        
    def quit(self):
        # 清理所有窗口
        if self.settings_window:
            self.settings_window.close()
        if self.hud_window:
            self.hud_window.close()
        if self.debug_window:
            self.debug_window.close()
        self.tray_icon.hide()
        self.app.quit()
        
    def show_splash_and_run(self):
        """显示启动动画后开始运行"""
        # 检查是否显示启动动画
        show_splash = settings_manager.get("general", "show_splash", True)

        if show_splash:
            # 创建并显示启动动画
            self.splash_window = SplashWindow()
            self.splash_window.finished.connect(self.on_splash_finished)
            self.splash_window.start()
        else:
            # 直接显示托盘图标
            self.tray_icon.show()

    def on_splash_finished(self):
        """启动动画完成后"""
        self.splash_window = None
        self.tray_icon.show()

    def run(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统不支持托盘图标")
            sys.exit(1)

        # 显示启动动画（如果启用）
        self.show_splash_and_run()

        sys.exit(self.app.exec())
