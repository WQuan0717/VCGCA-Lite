import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from src.tray_app import TrayApplication
from src.utils.single_instance import single_instance_checker

if __name__ == "__main__":
    # 检查是否已有实例在运行（在创建QApplication之前检查）
    if single_instance_checker.is_already_running():
        # 创建临时QApplication来显示消息框
        temp_app = QApplication(sys.argv)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("VCGCA-Lite")
        msg_box.setText("VCGCA-Lite 已经在运行中")
        msg_box.setInformativeText("程序已在系统托盘中运行，请勿重复启动。")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        sys.exit(0)
    
    try:
        # 启动程序
        app = TrayApplication()
        exit_code = app.run()
        sys.exit(exit_code)
    finally:
        # 确保释放互斥体
        single_instance_checker.release()
