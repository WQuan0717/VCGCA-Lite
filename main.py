import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    # 在加载用户设置之前进入隔离检查；同一入口用于验证冻结后的程序。
    if "--check-environment" in sys.argv:
        sys.argv.remove("--check-environment")
        try:
            from scripts.check_environment import main as check_environment
            check_environment()
            return 0
        except Exception as error:
            # windowed EXE 没有控制台，检查失败也写报告，避免弹窗阻塞自动验证。
            if "--report" in sys.argv:
                import json
                import traceback
                from pathlib import Path
                report_path = Path(sys.argv[sys.argv.index("--report") + 1])
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(json.dumps({
                    "status": "failed", "error": str(error),
                    "traceback": traceback.format_exc(),
                }, ensure_ascii=False, indent=2), encoding="utf-8")
            return 1

    from PyQt6.QtWidgets import QApplication, QMessageBox
    from src.tray_app import TrayApplication
    from src.utils.single_instance import single_instance_checker

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
        return 0
    
    try:
        # 启动程序
        app = TrayApplication()
        return app.run()
    finally:
        # 确保释放互斥体
        single_instance_checker.release()


if __name__ == "__main__":
    sys.exit(main())
