"""
系统控制功能模块
实现Windows系统的各种控制功能
"""

import os
import datetime
from pathlib import Path
import ctypes
from ctypes import cast, POINTER
import pyautogui
from PIL import ImageGrab


class SystemController:
    """系统控制器 - 提供Windows系统控制功能"""

    # 可用的控制功能列表 - key为英文(内部使用), value为中文显示名称
    AVAILABLE_ACTIONS = {
        "screenshot": "截屏并保存",
        "mute_toggle": "静音/取消静音",
        "volume_up": "增大音量",
        "volume_down": "减小音量",
        "show_desktop": "显示桌面",
    }

    def __init__(self):
        """初始化系统控制器"""
        self.screenshot_dir = Path.home() / "Pictures" / "VCGCA-Screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_action_display_name(cls, action_key):
        """获取控制功能的显示名称(用于UI显示)"""
        return cls.AVAILABLE_ACTIONS.get(action_key, action_key)

    @classmethod
    def get_all_action_keys(cls):
        """获取所有控制功能的key列表"""
        return list(cls.AVAILABLE_ACTIONS.keys())

    def execute_action(self, action_key):
        """执行指定的控制功能"""
        action_map = {
            "screenshot": self.take_screenshot,
            "mute_toggle": self.toggle_mute,
            "volume_up": self.increase_volume,
            "volume_down": self.decrease_volume,
            "show_desktop": self.show_desktop,
        }

        action_func = action_map.get(action_key)
        if action_func:
            try:
                action_func()
                display_name = self.get_action_display_name(action_key)
                return True, f"执行成功: {display_name}"
            except Exception as e:
                return False, f"执行失败: {e}"
        else:
            return False, f"未知控制功能: {action_key}"

    def take_screenshot(self):
        """截屏并保存"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.screenshot_dir / filename

        # 使用PIL截取屏幕
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        print(f"截图已保存: {filepath}")
        return str(filepath)

    def toggle_mute(self):
        """静音/取消静音切换 - 使用Windows API"""
        # 使用Windows多媒体API
        WM_APPCOMMAND = 0x319
        APPCOMMAND_VOLUME_MUTE = 0x80000
        
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.SendMessageW(hwnd, WM_APPCOMMAND, 0, APPCOMMAND_VOLUME_MUTE)
        print("静音/取消静音切换")

    def increase_volume(self):
        """增大音量 - 使用Windows API"""
        WM_APPCOMMAND = 0x319
        APPCOMMAND_VOLUME_UP = 0xA0000
        
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.SendMessageW(hwnd, WM_APPCOMMAND, 0, APPCOMMAND_VOLUME_UP)
        print("音量增大")

    def decrease_volume(self):
        """减小音量 - 使用Windows API"""
        WM_APPCOMMAND = 0x319
        APPCOMMAND_VOLUME_DOWN = 0x90000
        
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.SendMessageW(hwnd, WM_APPCOMMAND, 0, APPCOMMAND_VOLUME_DOWN)
        print("音量减小")

    def show_desktop(self):
        """显示桌面"""
        # 使用Windows API发送Win+D快捷键
        pyautogui.keyDown('win')
        pyautogui.keyDown('d')
        pyautogui.keyUp('d')
        pyautogui.keyUp('win')
        print("显示桌面")


# 全局系统控制器实例
system_controller = SystemController()
