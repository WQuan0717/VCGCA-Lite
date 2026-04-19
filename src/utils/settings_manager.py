import json
import os
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
                "show_splash": True
            },
            "display": {
                "opacity": 80,
                "position": "右上"
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
                    # 合并加载的配置和默认配置
                    self._settings = self._merge_settings(self._defaults.copy(), loaded)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载设置失败: {e}，使用默认设置")
                self._settings = self._defaults.copy()
        else:
            self._settings = self._defaults.copy()
            self.save_settings()
    
    def _merge_settings(self, defaults, loaded):
        """递归合并设置，确保所有默认键都存在"""
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_settings(self):
        """保存设置到文件"""
        self._ensure_config_dir()
        
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=4)
            return True
        except IOError as e:
            print(f"保存设置失败: {e}")
            return False
    
    def get(self, section, key, default=None):
        """获取设置值"""
        if section in self._settings and key in self._settings[section]:
            return self._settings[section][key]
        return default
    
    def set(self, section, key, value):
        """设置值"""
        if section not in self._settings:
            self._settings[section] = {}
        old_value = self._settings[section].get(key)
        self._settings[section][key] = value
        # 发送设置变更信号
        self.settings_changed.emit(section, key, value)
    
    def get_section(self, section):
        """获取整个section的配置"""
        return self._settings.get(section, {})
    
    def set_section(self, section, values):
        """设置整个section的配置"""
        self._settings[section] = values
    
    def get_all_settings(self):
        """获取所有设置"""
        return self._settings.copy()
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        self._settings = self._defaults.copy()
        self.save_settings()


# 全局设置管理器实例
settings_manager = SettingsManager()
