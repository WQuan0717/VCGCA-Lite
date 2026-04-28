import os
import sys
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt


def get_icon_path():
    """获取图标文件路径"""
    # 获取程序运行目录
    if getattr(sys, 'frozen', False):
        # 打包后的程序
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_path, 'assets', 'app.ico')


def create_default_icon(size=64):
    """创建一个默认的托盘图标（当没有自定义图标时使用）"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 绘制圆形背景
    painter.setBrush(QBrush(QColor(52, 152, 219)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, size-8, size-8)
    
    # 绘制文字
    painter.setPen(QColor(255, 255, 255))
    font = painter.font()
    font.setPointSize(24)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "V")
    
    painter.end()
    return QIcon(pixmap)


def get_application_icon():
    """获取应用程序图标，优先使用自定义图标"""
    icon_path = get_icon_path()
    
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    else:
        # 如果没有自定义图标，使用默认生成的图标
        return create_default_icon()
