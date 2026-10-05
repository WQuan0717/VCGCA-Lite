import json
import os
import tempfile
from copy import deepcopy
from PyQt6.QtCore import QObject, pyqtSignal


class SettingsManager(QObject):
    _instance = None
    settings_changed = pyqtSignal(str, str, object)  # section, key, value
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super().__init__()
        self._initialized = True
        self._config_dir = os.path.join(os.path.expanduser("~"), ".vcgca-lite")
        self._config_file = os.path.join(self._config_dir, "settings.json")
        
        # 默认配置
        self._defaults = {
            "general": {
                "auto_start": False,
                "show_splash": True,
                "copy_to_clipboard": False,
                "screenshot_path": "",
                "show_open_folder": True
            },
            "display": {
                "opacity": 80,
                "width": 300,
                "height": 150,
                "h_position": 100,
                "v_position": 0,
                "hud_enabled": True
            },
            "gesture": {
                "prepare_time": 1000,
                "change_time": 1000,
                "cooldown_time": 2000,
                "mappings": [
                    {"prepare": "Open_Palm", "response": "Closed_Fist", "action": "screenshot"},
                    {"prepare": "Open_Palm", "response": "Thumb_Up", "action": "volume_up"},
                    {"prepare": "Open_Palm", "response": "Thumb_Down", "action": "volume_down"},
                    {"prepare": "Victory", "response": "Pointing_Up", "action": "show_desktop"}
                ]
            },
            "advanced": {
                "debug_mode": False,
                "log_to_file": False
            }
        }
        
        self._settings = {}
        self.load_settings()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self._config_dir):
            os.makedirs(self._config_dir)
    
    def load_settings(self):
        """从文件加载设置"""
        self._ensure_config_dir()
        
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                if not isinstance(loaded, dict):
                    raise ValueError("配置文件必须是 JSON 对象")
                # 合并加载的配置和默认配置
                self._settings = self._merge_settings(self._defaults, loaded)
            except (ValueError, OSError) as e:
                print(f"加载设置失败: {e}，使用默认设置")
                self._settings = deepcopy(self._defaults)
        else:
            self._settings = deepcopy(self._defaults)
            self.save_settings()
    
    def _merge_settings(self, defaults, loaded):
        """递归合并设置，确保所有默认键都存在"""
        result = deepcopy(defaults)
        for key, value in loaded.items():
            if key in defaults and isinstance(defaults[key], dict):
                if isinstance(value, dict):
                    result[key] = self._merge_settings(defaults[key], value)
            elif key in defaults and type(value) is not type(defaults[key]):
                continue
            else:
                result[key] = deepcopy(value)
        return result
    
    def save_settings(self):
        """保存设置到文件"""
        temporary_path = None
        try:
            self._ensure_config_dir()
            # 在同一目录写临时文件后替换，避免失败时破坏已有配置。
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                    dir=os.path.dirname(self._config_file), prefix='settings-',
                    suffix='.tmp', delete=False) as f:
                temporary_path = f.name
                json.dump(self._settings, f, ensure_ascii=False, indent=4)
            os.replace(temporary_path, self._config_file)
            return True
        except (OSError, TypeError, ValueError) as e:
            print(f"保存设置失败: {e}")
            return False
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)
    
    def get(self, section, key, default=None):
        """获取设置值"""
        if section in self._settings and key in self._settings[section]:
            return deepcopy(self._settings[section][key])
        return deepcopy(default)
    
    def set(self, section, key, value):
        """设置值"""
        if section not in self._settings:
            self._settings[section] = {}
        if self._settings[section].get(key) == value:
            return
        self._settings[section][key] = deepcopy(value)
        # 发送设置变更信号
        self.settings_changed.emit(section, key, deepcopy(value))
    
    def get_section(self, section):
        """获取整个section的配置"""
        return deepcopy(self._settings.get(section, {}))
    
    def set_section(self, section, values):
        """设置整个section的配置"""
        self._settings[section] = deepcopy(values)
    
    def get_all_settings(self):
        """获取所有设置"""
        return deepcopy(self._settings)
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        self._settings = deepcopy(self._defaults)
        self.save_settings()


# 全局设置管理器实例
settings_manager = SettingsManager()
