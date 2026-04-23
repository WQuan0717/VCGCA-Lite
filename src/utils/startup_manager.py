"""
开机启动管理器
管理 Windows 开机启动项
"""

import os
import sys
import winreg
from pathlib import Path


class StartupManager:
    """管理应用程序的开机启动"""

    # 注册表路径
    RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "VCGCA-Lite"

    @staticmethod
    def get_executable_path():
        """获取当前可执行文件的完整路径"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的 exe
            return sys.executable
        else:
            # 如果是开发环境
            return os.path.abspath(sys.argv[0])

    @staticmethod
    def is_auto_start_enabled():
        """检查开机启动是否已启用"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, StartupManager.RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, StartupManager.APP_NAME)
                    return value == StartupManager.get_executable_path()
                except FileNotFoundError:
                    return False
        except Exception as e:
            print(f"检查开机启动状态失败: {e}")
            return False

    @staticmethod
    def enable_auto_start():
        """启用开机启动"""
        try:
            exe_path = StartupManager.get_executable_path()

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, StartupManager.RUN_KEY_PATH, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, StartupManager.APP_NAME, 0, winreg.REG_SZ, exe_path)

            print(f"已启用开机启动: {exe_path}")
            return True
        except Exception as e:
            print(f"启用开机启动失败: {e}")
            return False

    @staticmethod
    def disable_auto_start():
        """禁用开机启动"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, StartupManager.RUN_KEY_PATH, 0, winreg.KEY_WRITE) as key:
                try:
                    winreg.DeleteValue(key, StartupManager.APP_NAME)
                    print("已禁用开机启动")
                    return True
                except FileNotFoundError:
                    # 本来就不存在，也算成功
                    return True
        except Exception as e:
            print(f"禁用开机启动失败: {e}")
            return False

    @staticmethod
    def toggle_auto_start(enable: bool):
        """切换开机启动状态"""
        if enable:
            return StartupManager.enable_auto_start()
        else:
            return StartupManager.disable_auto_start()
