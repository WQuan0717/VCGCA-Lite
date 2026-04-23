"""
日志系统
提供文件日志记录、日志级别控制、日志查看功能
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class LogManager(QObject):
    """日志管理器"""

    # 信号：新日志消息
    new_log_message = pyqtSignal(str, str)  # level, message

    # 日志级别映射
    LEVEL_MAP = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    def __init__(self):
        super().__init__()

        # 日志目录
        self.log_dir = Path.home() / '.vcgca-lite' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 当前日志文件
        self.current_log_file = self.log_dir / f"vcgca-lite-{datetime.now().strftime('%Y%m%d')}.log"

        # 创建 logger
        self.logger = logging.getLogger('VCGCA-Lite')
        self.logger.setLevel(logging.DEBUG)

        # 清除旧的处理器
        self.logger.handlers.clear()

        # 文件处理器（按天轮转，保留7天）
        file_handler = logging.handlers.TimedRotatingFileHandler(
            self.current_log_file,
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # 格式化器
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 自定义处理器，发送信号
        self.signal_handler = SignalHandler(self)
        self.signal_handler.setLevel(logging.DEBUG)
        self.signal_handler.setFormatter(formatter)
        self.logger.addHandler(self.signal_handler)

        self.info("日志系统初始化完成")

    def debug(self, message):
        """记录 DEBUG 级别日志"""
        self.logger.debug(message)

    def info(self, message):
        """记录 INFO 级别日志"""
        self.logger.info(message)

    def warning(self, message):
        """记录 WARNING 级别日志"""
        self.logger.warning(message)

    def error(self, message):
        """记录 ERROR 级别日志"""
        self.logger.error(message)

    def critical(self, message):
        """记录 CRITICAL 级别日志"""
        self.logger.critical(message)

    def set_level(self, level):
        """设置日志级别"""
        if level in self.LEVEL_MAP:
            self.logger.setLevel(self.LEVEL_MAP[level])
            self.info(f"日志级别设置为: {level}")

    def get_log_files(self):
        """获取所有日志文件列表"""
        log_files = []
        if self.log_dir.exists():
            for f in sorted(self.log_dir.glob('vcgca-lite-*.log'), reverse=True):
                log_files.append({
                    'name': f.name,
                    'path': str(f),
                    'size': f.stat().st_size,
                    'modified': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        return log_files

    def read_log_file(self, log_path, lines=100):
        """读取日志文件内容"""
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e:
            return f"读取日志文件失败: {e}"

    def clear_old_logs(self, days=7):
        """清理旧日志文件"""
        try:
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=days)

            count = 0
            for f in self.log_dir.glob('vcgca-lite-*.log'):
                if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                    f.unlink()
                    count += 1

            self.info(f"清理了 {count} 个旧日志文件")
            return count
        except Exception as e:
            self.error(f"清理日志文件失败: {e}")
            return 0


class SignalHandler(logging.Handler):
    """自定义日志处理器，发送 Qt 信号"""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def emit(self, record):
        """发送日志信号"""
        msg = self.format(record)
        self.manager.new_log_message.emit(record.levelname, msg)


# 全局日志管理器实例
log_manager = LogManager()
