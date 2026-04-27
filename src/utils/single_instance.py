"""
单实例运行检测
防止程序被多次启动
"""

import ctypes
from ctypes import wintypes


class SingleInstanceChecker:
    """Windows 互斥体实现的单实例检测"""
    
    def __init__(self, mutex_name="VCGCA-Lite-SingleInstance"):
        self.mutex_name = mutex_name
        self.mutex_handle = None
        
    def is_already_running(self):
        """检查程序是否已经在运行
        
        Returns:
            True: 已有实例在运行
            False: 没有实例在运行，可以启动
        """
        # 尝试创建命名互斥体
        self.mutex_handle = ctypes.windll.kernel32.CreateMutexW(
            None,  # 默认安全属性
            False,  # 不立即拥有
            self.mutex_name  # 互斥体名称
        )
        
        # 获取错误码
        error = ctypes.windll.kernel32.GetLastError()
        
        # ERROR_ALREADY_EXISTS = 183
        if error == 183:
            # 互斥体已存在，说明已有实例在运行
            self._close_mutex()
            return True
        
        # 互斥体创建成功，说明没有实例在运行
        return False
    
    def _close_mutex(self):
        """关闭互斥体句柄"""
        if self.mutex_handle:
            ctypes.windll.kernel32.CloseHandle(self.mutex_handle)
            self.mutex_handle = None
    
    def release(self):
        """程序退出时释放互斥体"""
        self._close_mutex()


# 全局单实例检测器
single_instance_checker = SingleInstanceChecker()
