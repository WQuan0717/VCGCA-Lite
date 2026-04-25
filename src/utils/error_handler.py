"""
简化错误处理器
- 捕获未处理异常
- 将异常信息存入日志
"""

import sys
import traceback
from PyQt6.QtCore import QObject, pyqtSignal

from src.utils.logger import log_manager


class ErrorHandler(QObject):
    """简化错误处理器"""

    def __init__(self):
        super().__init__()
        self.original_excepthook = None

    def install_global_handler(self):
        """安装全局异常处理器"""
        self.original_excepthook = sys.excepthook
        sys.excepthook = self._handle_exception
        log_manager.info("错误处理器已启动")

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        # 格式化异常信息
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # 记录到日志
        log_manager.critical("=" * 50)
        log_manager.critical("程序发生未捕获的异常:")
        log_manager.critical(error_msg)
        log_manager.critical("=" * 50)

        # 调用原始的异常处理器（显示错误对话框）
        if self.original_excepthook:
            self.original_excepthook(exc_type, exc_value, exc_traceback)


# 全局错误处理器实例
error_handler = ErrorHandler()
