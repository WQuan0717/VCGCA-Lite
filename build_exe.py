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
app_name_with_version = f"{APP_NAME}-v{version}"

# 输出目录
output_dir = os.path.join(project_root, "output")
dist_dir = os.path.join(output_dir, "dist")

# 检查旧EXE文件
old_exe_name = f"{APP_NAME}.exe"
new_exe_name = f"{app_name_with_version}.exe"
old_exe_path = os.path.join(project_root, "dist", old_exe_name)
new_exe_path = os.path.join(project_root, "dist", new_exe_name)

# 如果同名EXE正在运行，尝试使用不同的输出目录
if os.path.exists(new_exe_path):
    try:
        os.rename(new_exe_path, new_exe_path + ".bak")
        os.remove(new_exe_path + ".bak")
    except:
        print(f"警告: 无法删除旧的EXE文件，可能正在运行")
        print(f"将构建到 output/dist 目录")
        os.makedirs(dist_dir, exist_ok=True)
        final_dist_dir = dist_dir
else:
    final_dist_dir = os.path.join(project_root, "dist")

# PyInstaller 参数
args = [
    'main.py',                          # 主程序入口
    f'--name={app_name_with_version}',  # 程序名称（带版本号）
    '--onefile',                        # 打包成单个exe文件
    '--windowed',                       # 不显示控制台窗口
    '--noconfirm',                      # 覆盖输出目录
    '--clean',                          # 清理临时文件

    # 添加数据文件
    f'--add-data={os.path.join(project_root, "src")};src',

    # 隐藏导入
    '--hidden-import=src.tray_app',
    '--hidden-import=src.windows.settings_window',
    '--hidden-import=src.windows.hud_window',
    '--hidden-import=src.windows.debug_window',
    '--hidden-import=src.windows.splash_window',
    '--hidden-import=src.utils.icon_helper',
    '--hidden-import=src.utils.settings_manager',
    '--hidden-import=src.utils.version',

    # 图标（如果有的话）
    # '--icon=icon.ico',

    # 输出目录
    f'--distpath={final_dist_dir}',
    f'--workpath={os.path.join(project_root, "build")}',
    f'--specpath={project_root}',
]

print("=" * 50)
print(f"开始构建 EXE...")
print(f"应用名称: {APP_NAME}")
print(f"版本号: v{version}")
print(f"输出文件名: {new_exe_name}")
print(f"项目目录: {project_root}")
print(f"输出目录: {final_dist_dir}")
print("=" * 50)

PyInstaller.__main__.run(args)

print("=" * 50)
print(f"构建完成!")
print(f"EXE文件: {os.path.join(final_dist_dir, new_exe_name)}")
print("=" * 50)
