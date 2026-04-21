"""
手势名称中英文映射
"""

# MediaPipe手势名称到中文的映射
GESTURE_NAME_MAP = {
    "None": "无",
    "Closed_Fist": "握拳",
    "Open_Palm": "张开手掌",
    "Pointing_Up": "指向上方",
    "Thumb_Down": "拇指向下",
    "Thumb_Up": "拇指向上",
    "Victory": "胜利手势",
    "ILoveYou": "我爱你手势",
}

# 反向映射（中文到英文）
GESTURE_NAME_MAP_REVERSE = {v: k for k, v in GESTURE_NAME_MAP.items()}


def get_gesture_display_name(english_name):
    """获取手势的中文显示名称"""
    return GESTURE_NAME_MAP.get(english_name, english_name)


def get_gesture_english_name(chinese_name):
    """根据中文名称获取英文名称"""
    return GESTURE_NAME_MAP_REVERSE.get(chinese_name, chinese_name)


def get_all_gesture_display_names():
    """获取所有手势的中文显示名称列表"""
    return list(GESTURE_NAME_MAP.values())


def get_all_gesture_english_names():
    """获取所有手势的英文名称列表"""
    return list(GESTURE_NAME_MAP.keys())
