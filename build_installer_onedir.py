#!/usr/bin/env python3
"""
VCGCA-Lite 安装包构建脚本 - onedir 模式
构建目录版 EXE 并生成安装程序
"""

import os
import sys
import subprocess
import shutil

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.utils.version import get_version_string, APP_NAME

# 配置
INNO_SETUP_PATH = os.environ.get("INNO_SETUP_PATH") or shutil.which("ISCC.exe")
if not INNO_SETUP_PATH:
    for base_dir in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"),
                     r"D:\Program Files (x86)"):
        if base_dir:
            candidate = os.path.join(base_dir, "Inno Setup 6", "ISCC.exe")
            if os.path.isfile(candidate):
                INNO_SETUP_PATH = candidate
                break
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ONEDIR_DIST = os.path.join(PROJECT_ROOT, "output", "onedir", APP_NAME)
INSTALLER_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "installer_output")

def check_inno_setup():
    """检查 Inno Setup 是否安装"""
    if not INNO_SETUP_PATH or not os.path.isfile(INNO_SETUP_PATH):
        print("错误: 未找到 Inno Setup 6。请安装它，或将 INNO_SETUP_PATH 设置为 ISCC.exe 的完整路径。")
        return False
    return True

def build_exe_onedir():
    """构建 onedir 版 EXE"""
    print("=" * 60)
    print("步骤 1: 构建 onedir 版 EXE")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, "build_exe_onedir.py"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=False
        )
        print("✓ EXE 构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ EXE 构建失败: {e}")
        return False

def build_installer():
    """使用 Inno Setup 构建安装包"""
    print("\n" + "=" * 60)
    print("步骤 2: 构建安装包")
    print("=" * 60)
    
    # 检查安装脚本
    iss_file = os.path.join(PROJECT_ROOT, "installer_onedir.iss")
    if not os.path.exists(iss_file):
        print(f"错误: 未找到安装脚本: {iss_file}")
        return False
    
    # 保留其他版本安装包，只由编译器覆盖本次版本的文件。
    os.makedirs(INSTALLER_OUTPUT_DIR, exist_ok=True)
    
    try:
        result = subprocess.run(
            [INNO_SETUP_PATH, f"/DMyAppVersion={get_version_string()}", "installer_onedir.iss"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=False
        )
        print("✓ 安装包构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 安装包构建失败: {e}")
        return False

def show_result():
    """显示构建结果"""
    print("\n" + "=" * 60)
    print("构建完成")
    print("=" * 60)
    
    version = get_version_string()
    installer_name = f"VCGCA-Lite-Setup-v{version}.exe"
    installer_path = os.path.join(INSTALLER_OUTPUT_DIR, installer_name)
    
    if os.path.exists(installer_path):
        file_size = os.path.getsize(installer_path) / (1024 * 1024)  # MB
        print(f"\n✓ 安装包已生成:")
        print(f"  文件: {installer_path}")
        print(f"  大小: {file_size:.2f} MB")
        print(f"\n可以分发给用户进行安装")
    else:
        print("\n✗ 未找到生成的安装包")
        return False
    
    return True

def main():
    """主函数"""
    print("VCGCA-Lite onedir 模式安装包构建工具")
    print(f"版本: {get_version_string()}")
    print()
    
    # 检查 Inno Setup
    if not check_inno_setup():
        sys.exit(1)
    
    # 构建 EXE
    if not build_exe_onedir():
        sys.exit(1)
    
    # 构建安装包
    if not build_installer():
        sys.exit(1)
    
    # 显示结果
    if not show_result():
        sys.exit(1)
    
    print("\n✓ 所有步骤完成！")

if __name__ == "__main__":
    main()
