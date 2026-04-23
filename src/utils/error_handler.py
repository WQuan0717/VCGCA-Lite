"""
错误处理与恢复系统
提供全局异常捕获、崩溃报告、自动恢复功能
"""

import sys
import os
import traceback
import datetime
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox


class ErrorHandler(QObject):
    """全局错误处理器"""

    # 信号：发生严重错误
    critical_error = pyqtSignal(str, str)  # 错误类型, 错误信息

    def __init__(self):
        super().__init__()

        # 错误报告目录
        self.crash_dir = Path.home() / '.vcgca-lite' / 'crashes'
        self.crash_dir.mkdir(parents=True, exist_ok=True)

        # 最大保留的崩溃报告数量
        self.max_crash_reports = 10

        # 是否已处理异常（防止递归）
        self._handling_exception = False

    def install_global_handler(self):
        """安装全局异常处理器"""
        sys.excepthook = self._global_exception_handler

    def _global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """全局异常处理器"""
        # 防止递归处理
        if self._handling_exception:
            return

        self._handling_exception = True

        # 格式化错误信息
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # 记录错误
        self._log_crash(exc_type.__name__, error_msg)

        # 显示错误对话框
        self._show_error_dialog(exc_type.__name__, str(exc_value), error_msg)

        # 发射信号
        self.critical_error.emit(exc_type.__name__, str(exc_value))

        self._handling_exception = False

    def _log_crash(self, error_type, error_msg):
        """记录崩溃日志"""
        try:
            # 生成崩溃报告文件名
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            crash_file = self.crash_dir / f"crash_{timestamp}.txt"

            # 写入崩溃信息
            with open(crash_file, 'w', encoding='utf-8') as f:
                f.write(f"VCGCA-Lite 崩溃报告\n")
                f.write(f"{'=' * 50}\n")
                f.write(f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"错误类型: {error_type}\n")
                f.write(f"{'=' * 50}\n\n")
                f.write(error_msg)

            print(f"崩溃报告已保存: {crash_file}")

            # 清理旧报告
            self._cleanup_old_reports()

        except Exception as e:
            print(f"保存崩溃报告失败: {e}")

    def _cleanup_old_reports(self):
        """清理旧的崩溃报告"""
        try:
            crash_files = sorted(self.crash_dir.glob('crash_*.txt'),
                                 key=lambda x: x.stat().st_mtime,
                                 reverse=True)

            # 删除超出数量的旧报告
            for old_file in crash_files[self.max_crash_reports:]:
                old_file.unlink()
                print(f"删除旧崩溃报告: {old_file.name}")

        except Exception as e:
            print(f"清理旧崩溃报告失败: {e}")

    def _show_error_dialog(self, error_type, error_msg, full_traceback):
        """显示错误对话框"""
        try:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("VCGCA-Lite - 发生错误")
            msg_box.setIcon(QMessageBox.Icon.Critical)

            # 简化错误信息
            short_msg = error_msg[:100] + "..." if len(error_msg) > 100 else error_msg

            msg_box.setText(f"程序发生错误: {error_type}")
            msg_box.setInformativeText(f"{short_msg}\n\n错误报告已保存到:\n{self.crash_dir}")

            # 添加详细按钮
            msg_box.setDetailedText(full_traceback)

            # 添加按钮
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Ok |
                QMessageBox.StandardButton.Retry
            )
            msg_box.button(QMessageBox.StandardButton.Retry).setText("尝试恢复")

            result = msg_box.exec()

            if result == QMessageBox.StandardButton.Retry:
                self._attempt_recovery()

        except Exception as e:
            print(f"显示错误对话框失败: {e}")

    def _attempt_recovery(self):
        """尝试恢复程序"""
        print("尝试恢复程序...")
        try:
            # 1. 清理临时资源
            self._cleanup_resources()

            # 2. 重置关键组件
            self._reset_components()

            # 3. 重新初始化
            self._reinitialize()

            print("程序恢复成功")

        except Exception as e:
            print(f"程序恢复失败: {e}")
            # 如果恢复失败，建议重启
            QMessageBox.warning(
                None,
                "恢复失败",
                "自动恢复失败，请手动重启程序。"
            )

    def _cleanup_resources(self):
        """清理临时资源"""
        try:
            # 清理手势识别服务
            from src.core.gesture_service import gesture_service
            if gesture_service.isRunning():
                gesture_service.stop()
                print("已停止手势识别服务")
        except Exception as e:
            print(f"清理资源失败: {e}")

    def _reset_components(self):
        """重置关键组件"""
        try:
            # 重置手势控制器状态
            from src.core.gesture_controller import gesture_controller
            gesture_controller._reset_to_idle("错误恢复")
            print("已重置手势控制器")
        except Exception as e:
            print(f"重置组件失败: {e}")

    def _reinitialize(self):
        """重新初始化"""
        try:
            # 重新启动手势识别服务
            from src.core.gesture_service import gesture_service
            if not gesture_service.isRunning():
                gesture_service.initialize()
                gesture_service.start()
                print("已重新启动手势识别服务")
        except Exception as e:
            print(f"重新初始化失败: {e}")

    def get_crash_reports(self):
        """获取所有崩溃报告列表"""
        try:
            reports = []
            for f in sorted(self.crash_dir.glob('crash_*.txt'), reverse=True):
                reports.append({
                    'name': f.name,
                    'path': str(f),
                    'time': datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': f.stat().st_size
                })
            return reports
        except Exception as e:
            print(f"获取崩溃报告列表失败: {e}")
            return []

    def read_crash_report(self, report_path):
        """读取崩溃报告内容"""
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"读取崩溃报告失败: {e}"


# 全局错误处理器实例
error_handler = ErrorHandler()
