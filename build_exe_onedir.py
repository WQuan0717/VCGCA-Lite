#!/usr/bin/env python3
"""
VCGCA-Lite 构建脚本 - onedir 模式
构建成文件夹形式，启动更快
"""

import PyInstaller.__main__
import os
import shutil
import sys

# 添加项目路径以导入版本信息
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.utils.version import get_version_string, APP_NAME

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 获取版本号
version = get_version_string()
app_name = APP_NAME  # onedir 模式使用固定名称，不带版本号

# 输出目录
output_dir = os.path.join(project_root, "output", "onedir")
dist_dir = os.path.join(output_dir, app_name)

# 清理旧的构建
if os.path.exists(dist_dir):
    print(f"清理旧构建: {dist_dir}")
    shutil.rmtree(dist_dir)

# PyInstaller 参数
args = [
    'main.py',                          # 主程序入口
    f'--name={app_name}',               # 程序名称
    '--onedir',                         # 打包成文件夹（不是单文件）
    '--windowed',                       # 不显示控制台窗口
    '--noconfirm',                      # 覆盖输出目录
    '--clean',                          # 清理临时文件

    # 添加数据文件
    f'--add-data={os.path.join(project_root, "src")};src',

    # 隐藏导入 - 项目模块
    '--hidden-import=src.tray_app',
    '--hidden-import=src.windows.settings_window',
    '--hidden-import=src.windows.hud_window',
    '--hidden-import=src.windows.debug_window',
    '--hidden-import=src.windows.splash_window',
    '--hidden-import=src.utils.icon_helper',
    '--hidden-import=src.utils.settings_manager',
    '--hidden-import=src.utils.version',
    '--hidden-import=src.core.gesture_service',
    '--hidden-import=src.core.gesture_controller',
    '--hidden-import=src.core.system_control',
    '--hidden-import=src.utils.gesture_names',
    '--hidden-import=src.windows.gesture_mapping_dialog',

    # 隐藏导入 - MediaPipe 相关
    '--hidden-import=mediapipe',
    '--hidden-import=mediapipe.tasks',
    '--hidden-import=mediapipe.tasks.python',
    '--hidden-import=mediapipe.tasks.python.vision',
    '--hidden-import=mediapipe.tasks.python.core.base_options',
    '--hidden-import=mediapipe.tasks.python.components.containers',
    '--collect-all=mediapipe',

    # 输出目录
    f'--distpath={output_dir}',
    f'--workpath={os.path.join(project_root, "build_onedir")}',
    f'--specpath={project_root}',
]

print("=" * 60)
print(f"开始构建 (onedir 模式)...")
print(f"应用名称: {APP_NAME}")
print(f"版本号: v{version}")
print(f"输出目录: {dist_dir}")
print("=" * 60)

PyInstaller.__main__.run(args)

print("=" * 60)
print(f"构建完成!")
print(f"输出目录: {dist_dir}")
print(f"主程序: {os.path.join(dist_dir, f'{app_name}.exe')}")
print("=" * 60)
