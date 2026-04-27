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
import io


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
        self._screenshot_dir = None
        self._update_screenshot_dir()

    def _update_screenshot_dir(self):
        """更新截图保存目录（从设置读取）"""
        try:
            from src.utils.settings_manager import settings_manager
            custom_path = settings_manager.get("general", "screenshot_path", "")
            if custom_path:
                self._screenshot_dir = Path(custom_path)
            else:
                self._screenshot_dir = Path.home() / "Pictures" / "VCGCA-Screenshots"
        except Exception:
            self._screenshot_dir = Path.home() / "Pictures" / "VCGCA-Screenshots"

        # 确保目录存在
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)

    @property
    def screenshot_dir(self):
        """获取截图保存目录"""
        self._update_screenshot_dir()
        return self._screenshot_dir

    def get_screenshot_dir(self):
        """获取当前截图保存目录路径"""
        return str(self.screenshot_dir)

    @classmethod
    def get_action_display_name(cls, action_key):
        """获取控制功能的显示名称(用于UI显示)"""
        return cls.AVAILABLE_ACTIONS.get(action_key, action_key)

    @classmethod
    def get_all_action_keys(cls):
        """获取所有控制功能的key列表"""
        return list(cls.AVAILABLE_ACTIONS.keys())

    def execute_action(self, action_key, **kwargs):
        """执行指定的控制功能
        
        Args:
            action_key: 动作键名
            **kwargs: 额外参数（如copy_to_clipboard）
        """
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
                # 截图功能支持额外参数
                if action_key == "screenshot":
                    action_func(copy_to_clipboard=kwargs.get("copy_to_clipboard", False))
                else:
                    action_func()
                display_name = self.get_action_display_name(action_key)
                return True, f"执行成功: {display_name}"
            except Exception as e:
                return False, f"执行失败: {e}"
        else:
            return False, f"未知控制功能: {action_key}"

    def take_screenshot(self, copy_to_clipboard=False):
        """截屏并保存
        
        Args:
            copy_to_clipboard: 是否复制到剪贴板
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.screenshot_dir / filename

        # 使用PIL截取屏幕
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        print(f"截图已保存: {filepath}")
        
        # 复制到剪贴板
        if copy_to_clipboard:
            self._copy_image_to_clipboard(screenshot)
            print("截图已复制到剪贴板")
        
        return str(filepath)
    
    def _copy_image_to_clipboard(self, image):
        """将PIL图像复制到Windows剪贴板"""
        try:
            # 尝试使用 win32clipboard (更可靠)
            import win32clipboard
            from PIL import Image

            # 将图像转换为 BMP 格式（DIB）
            output = io.BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]  # 跳过 BMP 文件头
            output.close()

            # 打开剪贴板并设置数据
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            finally:
                win32clipboard.CloseClipboard()

        except ImportError:
            # 如果没有 win32clipboard，使用 ctypes 方式
            self._copy_image_to_clipboard_ctypes(image)
        except Exception as e:
            print(f"复制到剪贴板失败: {e}")

    def _copy_image_to_clipboard_ctypes(self, image):
        """使用 ctypes 将PIL图像复制到Windows剪贴板（备用方法）"""
        try:
            # 将PIL图像转换为DIB格式用于剪贴板
            output = io.BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]  # 跳过BMP文件头
            output.close()

            # 打开剪贴板
            CF_DIB = 8
            GHND = 0x0042  # GMEM_MOVEABLE | GMEM_ZEROINIT

            if ctypes.windll.user32.OpenClipboard(None):
                try:
                    ctypes.windll.user32.EmptyClipboard()

                    # 分配可移动内存
                    h_mem = ctypes.windll.kernel32.GlobalAlloc(GHND, len(data))
                    if h_mem:
                        p_mem = ctypes.windll.kernel32.GlobalLock(h_mem)
                        if p_mem:
                            ctypes.memmove(p_mem, data, len(data))
                            ctypes.windll.kernel32.GlobalUnlock(h_mem)
                            # SetClipboardData 会接管内存所有权，不需要释放
                            ctypes.windll.user32.SetClipboardData(CF_DIB, h_mem)
                finally:
                    ctypes.windll.user32.CloseClipboard()
        except Exception as e:
            print(f"复制到剪贴板失败: {e}")

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
