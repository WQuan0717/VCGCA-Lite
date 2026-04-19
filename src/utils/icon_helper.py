from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt


def create_default_icon(size=64):
    """创建一个默认的托盘图标"""
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
