#!/usr/bin/env python3
"""
视觉手势控制系统构建脚本 - onedir 模式
构建成文件夹形式，启动更快
"""

import PyInstaller.__main__
import os
import shutil
import sys
import tempfile
from pathlib import Path

# 只扫描当前环境、Qt 与系统目录，避免从宿主工具的 PATH 收集同名不兼容 DLL。
system_root = Path(os.environ.get('SystemRoot', r'C:\Windows'))
build_dll_dirs = [
    Path(sys.prefix) / 'Lib' / 'site-packages' / 'PySide6',
    Path(sys.prefix) / 'Library' / 'bin',
    Path(sys.prefix), system_root / 'System32', system_root,
]
os.environ['PATH'] = os.pathsep.join(str(path) for path in build_dll_dirs if path.is_dir())

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo, StringFileInfo, StringStruct, StringTable,
    VarFileInfo, VarStruct, VSVersionInfo,
)

# 添加项目路径以导入版本信息
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.utils.version import (APP_DESCRIPTION, APP_EXECUTABLE_NAME, APP_NAME,
                               COPYRIGHT, get_full_version_info, get_version_string)

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 获取版本号
version = get_version_string()
app_name = APP_EXECUTABLE_NAME  # 文件名使用稳定的英文标识，不带版本号

# 输出目录
output_dir = os.path.join(project_root, "output", "onedir")
dist_dir = os.path.join(output_dir, app_name)

# 清理旧的构建
if os.path.exists(dist_dir):
    resolved_dist = Path(dist_dir).resolve()
    resolved_output = Path(output_dir).resolve()
    if resolved_dist == resolved_output or not resolved_dist.is_relative_to(resolved_output):
        raise RuntimeError("拒绝清理输出目录以外的路径")
    print(f"清理旧构建: {dist_dir}")
    shutil.rmtree(resolved_dist)

# Windows 文件属性与应用、安装包共用版本来源。
version_details = get_full_version_info()
version_tuple = (version_details['major'], version_details['minor'], version_details['patch'], 0)
version_info = VSVersionInfo(
    ffi=FixedFileInfo(filevers=version_tuple, prodvers=version_tuple,
                     mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0, 0)),
    kids=[StringFileInfo([StringTable('080404b0', [
        StringStruct('FileDescription', APP_DESCRIPTION),
        StringStruct('FileVersion', version),
        StringStruct('ProductName', APP_NAME),
        StringStruct('ProductVersion', version),
        StringStruct('OriginalFilename', f'{APP_EXECUTABLE_NAME}.exe'),
        StringStruct('InternalName', APP_EXECUTABLE_NAME),
        StringStruct('LegalCopyright', COPYRIGHT),
    ])]), VarFileInfo([VarStruct('Translation', [0x0804, 1200])])],
)
version_file = Path(project_root) / 'build_onedir' / 'version_info.txt'
version_file.parent.mkdir(parents=True, exist_ok=True)
version_file.write_text(str(version_info), encoding='utf-8')

# PyInstaller 参数
args = [
    'main.py',                          # 主程序入口
    f'--name={app_name}',               # 程序名称
    '--onedir',                         # 打包成文件夹（不是单文件）
    '--windowed',                       # 不显示控制台窗口
    '--noconfirm',                      # 覆盖输出目录
    '--clean',                          # 清理临时文件
    f'--version-file={version_file}',

    # 应用程序图标
    f'--icon={os.path.join(project_root, "assets", "app.ico")}',

    # 添加数据文件
    f'--add-data={os.path.join(project_root, "src")};src',
    f'--add-data={os.path.join(project_root, "assets")};assets',

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
    '--hidden-import=scripts.check_environment',
    '--copy-metadata=opencv-contrib-python',

    # 隐藏导入 - MediaPipe 相关
    '--hidden-import=mediapipe',
    '--hidden-import=mediapipe.tasks',
    '--hidden-import=mediapipe.tasks.python',
    '--hidden-import=mediapipe.tasks.python.vision',
    '--hidden-import=mediapipe.tasks.python.core.base_options',
    '--hidden-import=mediapipe.tasks.python.components.containers',
    '--collect-all=mediapipe',
    # Prevent an unrelated binding or optional GPL diagnostic utility in the
    # build environment from being pulled into the distributed application.
    '--exclude-module=PyQt6',
    '--exclude-module=PyQt5',
    '--exclude-module=PySide2',
    '--exclude-module=mouseinfo',
    # MediaPipe imports its optional audio package, but this app is vision-only.
    # In particular, do not redistribute the optional ASIO-enabled DLLs.
    '--exclude-module=sounddevice',
    '--exclude-module=_sounddevice',
    '--exclude-module=_sounddevice_data',

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

# 依赖扫描可能导入应用模块；隔离用户目录，避免构建时创建真实配置和日志。
with tempfile.TemporaryDirectory(prefix="vision-build-") as isolated_home:
    home_variables = {key: os.environ.get(key) for key in ("USERPROFILE", "HOME")}
    try:
        os.environ["USERPROFILE"] = isolated_home
        os.environ["HOME"] = isolated_home
        PyInstaller.__main__.run(args)
    finally:
        for key, value in home_variables.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

# The application captures cameras only; it does not open media files or use
# Qt's optional software OpenGL renderer. Exclude those unused binary payloads
# and Qt's unused translations instead of redistributing unrelated components.
dist_root = Path(dist_dir).resolve()
unused_files = [dist_root / '_internal' / 'PySide6' / 'opengl32sw.dll']
unused_files.extend((dist_root / '_internal' / 'cv2').glob('opencv_videoio_ffmpeg*.dll'))
for unused in unused_files:
    if unused.exists():
        resolved = unused.resolve()
        if not resolved.is_relative_to(dist_root):
            raise RuntimeError("拒绝删除构建输出目录以外的文件")
        resolved.unlink()
translations = dist_root / '_internal' / 'PySide6' / 'translations'
if translations.exists():
    resolved = translations.resolve()
    if resolved == dist_root or not resolved.is_relative_to(dist_root):
        raise RuntimeError("拒绝清理构建输出目录以外的路径")
    shutil.rmtree(resolved)

# Source files are included for inspection; local interpreter caches can
# contain stale bytecode and machine-specific paths, so do not distribute them.
for cache_dir in (dist_root / '_internal' / 'src').rglob('__pycache__'):
    resolved = cache_dir.resolve()
    if not resolved.is_relative_to(dist_root):
        raise RuntimeError("拒绝清理构建输出目录以外的路径")
    shutil.rmtree(resolved)

# Put notices next to the executable so they survive portable distribution and
# are included verbatim by the installer.
for document in ('LICENSE', 'THIRD_PARTY_NOTICES.md'):
    shutil.copy2(Path(project_root) / document, dist_root / document)
shutil.copytree(Path(project_root) / 'third_party', dist_root / 'third_party')

print("=" * 60)
print(f"构建完成!")
print(f"输出目录: {dist_dir}")
print(f"主程序: {os.path.join(dist_dir, f'{app_name}.exe')}")
print("=" * 60)
