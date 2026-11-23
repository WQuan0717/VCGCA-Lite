"""User-facing notice for MediaPipe Tasks and its usage metrics."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMessageBox


NOTICE_VERSION = 1
PRIVACY_URL = "https://developers.google.com/edge/mediapipe/solutions/privacy"
NOTICE_HTML = (
    "<p>本程序使用 Google MediaPipe Tasks 识别手势。根据 Google 的说明，"
    "摄像头画面在本机处理，MediaPipe Tasks 可能向 Google 发送 API 使用和性能指标。</p>"
    f'<p>详情请阅读 <a href="{PRIVACY_URL}">MediaPipe Tasks 隐私说明</a>。</p>'
    "<p>同意后继续启动；不同意可退出。之后可以在托盘菜单中查看或撤回同意。</p>"
)


def _message_box(title, text):
    box = QMessageBox()
    box.setWindowTitle(title)
    box.setIcon(QMessageBox.Icon.Information)
    box.setTextFormat(Qt.TextFormat.RichText)
    box.setText(text)
    for label in box.findChildren(QLabel):
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    return box


def ensure_mediapipe_consent(settings):
    """Obtain consent before initializing MediaPipe, or leave it unstarted."""
    if settings.get("privacy", "mediapipe_notice_version", 0) == NOTICE_VERSION:
        return True
    box = _message_box("隐私说明", NOTICE_HTML)
    agree = box.addButton("同意并继续", QMessageBox.ButtonRole.AcceptRole)
    leave = box.addButton("退出", QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(leave)
    box.exec()
    if box.clickedButton() != agree:
        return False
    settings.set("privacy", "mediapipe_notice_version", NOTICE_VERSION)
    if settings.save_settings():
        return True
    settings.set("privacy", "mediapipe_notice_version", 0)
    QMessageBox.warning(None, "保存失败", "无法保存隐私选择，程序未启动。")
    return False


def review_mediapipe_consent(settings):
    """Return True only after successfully recording withdrawal of consent."""
    box = _message_box("隐私说明", NOTICE_HTML)
    revoke = box.addButton("撤回同意并退出", QMessageBox.ButtonRole.DestructiveRole)
    close = box.addButton("关闭", QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(close)
    box.exec()
    if box.clickedButton() != revoke:
        return False
    settings.set("privacy", "mediapipe_notice_version", 0)
    if settings.save_settings():
        return True
    settings.set("privacy", "mediapipe_notice_version", NOTICE_VERSION)
    QMessageBox.warning(None, "保存失败", "无法保存隐私选择，请重试。")
    return False
