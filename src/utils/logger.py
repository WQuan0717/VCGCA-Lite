"""
简化日志系统
- 单文件存储
- 保留最近2000条记录
- 代替print()输出
"""

import sys
import os
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class LogManager(QObject):
    """简化日志管理器"""

    # 信号：新日志消息 (level, message)
    new_log_message = pyqtSignal(str, str)

    # 最大保留日志条数
    MAX_LOG_LINES = 2000

    def __init__(self):
        super().__init__()

        # 日志目录
        self.log_dir = Path.home() / '.vcgca-lite'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 单一日志文件
        self.log_file = self.log_dir / 'app.log'

        # 内存中的日志缓存
        self.log_cache = []

        # 加载已有日志
        self._load_existing_logs()

        # 记录启动信息
        self.info("=" * 50)
        self.info("程序启动")
        self.info("=" * 50)

    def _load_existing_logs(self):
        """加载已有日志文件"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.log_cache = f.readlines()
                # 限制缓存大小
                if len(self.log_cache) > self.MAX_LOG_LINES:
                    self.log_cache = self.log_cache[-self.MAX_LOG_LINES:]
            except:
                self.log_cache = []

    def _write_log(self, level, message):
        """写入日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"

        # 添加到缓存
        self.log_cache.append(log_line)

        # 限制缓存大小，删除最早的
        if len(self.log_cache) > self.MAX_LOG_LINES:
            self.log_cache = self.log_cache[-self.MAX_LOG_LINES:]

        # 写入文件（覆盖写入所有缓存）
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.writelines(self.log_cache)
        except:
            pass

        # 发射信号
        self.new_log_message.emit(level, log_line.strip())

        # 同时输出到控制台
        print(log_line.strip())

    def debug(self, message):
        """调试日志"""
        self._write_log('DEBUG', message)

    def info(self, message):
        """信息日志"""
        self._write_log('INFO', message)

    def warning(self, message):
        """警告日志"""
        self._write_log('WARNING', message)

    def error(self, message):
        """错误日志"""
        self._write_log('ERROR', message)

    def critical(self, message):
        """严重错误日志"""
        self._write_log('CRITICAL', message)

    def get_all_logs(self):
        """获取所有日志"""
        return ''.join(self.log_cache)

    def clear_logs(self):
        """清空日志"""
        self.log_cache = []
        try:
            if self.log_file.exists():
                self.log_file.unlink()
        except:
            pass
        self.info("日志已清空")

    def get_log_file_path(self):
        """获取日志文件路径"""
        return str(self.log_file)


# 全局日志管理器实例
log_manager = LogManager()
