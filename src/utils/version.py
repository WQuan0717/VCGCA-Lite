"""
视觉手势控制系统版本与应用信息
"""

# 版本号 (遵循语义化版本规范)
VERSION_MAJOR = 1  # 主版本号：重大更新/不兼容修改
VERSION_MINOR = 0  # 次版本号：功能更新/向下兼容
VERSION_PATCH = 0  # 修订号：问题修复/向下兼容

# 版本后缀 (可选)
VERSION_SUFFIX = ""  # 例如："-alpha", "-beta", "-rc1"

# 完整版本号
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}{VERSION_SUFFIX}"

# 应用信息
APP_NAME = "视觉手势控制系统"
APP_DISPLAY_NAME = APP_NAME
APP_ENGLISH_NAME = "Vision-Based Gesture Control System"
# 文件名使用不含空格的英文标识；显示名称始终使用上面的完整中英文名称。
APP_EXECUTABLE_NAME = "VisionGestureControl"
APP_DESCRIPTION = "基于摄像头的实时手势识别与系统控制"

APP_DATA_DIR_NAME = ".vision-gesture-control"
STARTUP_REGISTRY_NAME = APP_EXECUTABLE_NAME
SINGLE_INSTANCE_MUTEX = "VisionGestureControl-SingleInstance"

# 版权信息
COPYRIGHT = "Copyright © 2026"
COMPANY = ""

# 开发者信息
DEVELOPER = "个人开发者"

# 构建信息
BUILD_DATE = "2026-11-23"

# 许可证
LICENSE = "MIT License"

# 项目链接
PROJECT_URL = "https://github.com/WQuan0717/VCGCA-Lite"


def get_version_string():
    """获取版本字符串"""
    return VERSION


def get_full_version_info():
    """获取完整版本信息"""
    return {
        "version": VERSION,
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "suffix": VERSION_SUFFIX,
        "app_name": APP_NAME,
        "app_display_name": APP_DISPLAY_NAME,
        "app_english_name": APP_ENGLISH_NAME,
        "description": APP_DESCRIPTION,
        "copyright": COPYRIGHT,
        "company": COMPANY,
        "developer": DEVELOPER,
        "build_date": BUILD_DATE,
        "license": LICENSE,
        "project_url": PROJECT_URL
    }
