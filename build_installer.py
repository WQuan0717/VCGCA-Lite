#!/usr/bin/env python3
"""
VCGCA-Lite 安装包构建脚本
自动构建 EXE 并生成安装程序
"""

import os
import sys
import subprocess
import shutil

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.utils.version import get_version_string, APP_NAME

# 配置
INNO_SETUP_PATH = r"D:\Program Files (x86)\Inno Setup 6\ISCC.exe"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
INSTALLER_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "installer_output")

def check_inno_setup():
    """检查 Inno Setup 是否安装"""
    if not os.path.exists(INNO_SETUP_PATH):
        print(f"错误: 未找到 Inno Setup，请确认安装路径: {INNO_SETUP_PATH}")
        print("请从 https://jrsoftware.org/isinfo.php 下载安装 Inno Setup 6")
        return False
    return True

def build_exe():
    """构建单文件 EXE"""
    print("=" * 60)
    print("步骤 1: 构建单文件 EXE")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, "build_exe.py"],
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
    iss_file = os.path.join(PROJECT_ROOT, "installer.iss")
    if not os.path.exists(iss_file):
        print(f"错误: 未找到安装脚本: {iss_file}")
        return False
    
    # 清理旧的安装包输出目录
    if os.path.exists(INSTALLER_OUTPUT_DIR):
        shutil.rmtree(INSTALLER_OUTPUT_DIR)
    os.makedirs(INSTALLER_OUTPUT_DIR, exist_ok=True)
    
    try:
        result = subprocess.run(
            [INNO_SETUP_PATH, "installer.iss"],
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
    print("VCGCA-Lite 安装包构建工具")
    print(f"版本: {get_version_string()}")
    print()
    
    # 检查 Inno Setup
    if not check_inno_setup():
        sys.exit(1)
    
    # 构建 EXE
    if not build_exe():
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
