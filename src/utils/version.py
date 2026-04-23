"""
VCGCA-Lite 版本信息
"""

# 版本号 (遵循语义化版本规范)
VERSION_MAJOR = 0  # 主版本号：重大更新/不兼容修改
VERSION_MINOR = 3  # 次版本号：功能更新/向下兼容
VERSION_PATCH = 1  # 修订号：问题修复/向下兼容

# 版本后缀 (可选)
VERSION_SUFFIX = ""  # 例如："-alpha", "-beta", "-rc1"

# 完整版本号
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}{VERSION_SUFFIX}"

# 应用信息
APP_NAME = "VCGCA-Lite"
APP_DISPLAY_NAME = "VCGCA-Lite"
APP_DESCRIPTION = "系统工具"

# 版权信息
COPYRIGHT = "Copyright © 2026"
COMPANY = "VCGCA"

# 开发者信息
DEVELOPER = "VCGCA Team"

# 构建信息
BUILD_DATE = "2026-04-21"

# 许可证
LICENSE = "MIT License"

# 项目链接
PROJECT_URL = "https://github.com/vcgca/vcgca-lite"


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
        "description": APP_DESCRIPTION,
        "copyright": COPYRIGHT,
        "company": COMPANY,
        "developer": DEVELOPER,
        "build_date": BUILD_DATE,
        "license": LICENSE,
        "project_url": PROJECT_URL
    }
