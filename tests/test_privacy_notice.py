import sys
from types import SimpleNamespace
from unittest.mock import Mock

import main
from src.utils import privacy_notice
from src.utils.settings_manager import settings_manager
from src.utils.single_instance import single_instance_checker


class FakeBox:
    def __init__(self, selected):
        self.selected = selected
        self.buttons = {}

    def addButton(self, label, role):
        self.buttons[label] = object()
        return self.buttons[label]

    def setDefaultButton(self, button):
        pass

    def exec(self):
        pass

    def clickedButton(self):
        return self.buttons[self.selected]


def test_declining_leaves_notice_unaccepted(monkeypatch):
    monkeypatch.setattr(privacy_notice, "_message_box", lambda *args: FakeBox("退出"))
    assert not privacy_notice.ensure_mediapipe_consent(settings_manager)
    assert settings_manager.get("privacy", "mediapipe_notice_version") == 0


def test_acceptance_is_saved_and_can_be_withdrawn(monkeypatch):
    monkeypatch.setattr(privacy_notice, "_message_box", lambda *args: FakeBox("同意并继续"))
    monkeypatch.setattr(settings_manager, "save_settings", lambda: True)
    assert privacy_notice.ensure_mediapipe_consent(settings_manager)
    assert settings_manager.get("privacy", "mediapipe_notice_version") == privacy_notice.NOTICE_VERSION
    monkeypatch.setattr(privacy_notice, "_message_box", lambda *args: FakeBox("撤回同意并退出"))
    assert privacy_notice.review_mediapipe_consent(settings_manager)
    assert settings_manager.get("privacy", "mediapipe_notice_version") == 0


def test_failed_save_does_not_start_with_unrecorded_consent(monkeypatch):
    monkeypatch.setattr(privacy_notice, "_message_box", lambda *args: FakeBox("同意并继续"))
    monkeypatch.setattr(settings_manager, "save_settings", lambda: False)
    monkeypatch.setattr(privacy_notice.QMessageBox, "warning", Mock())
    assert not privacy_notice.ensure_mediapipe_consent(settings_manager)
    assert settings_manager.get("privacy", "mediapipe_notice_version") == 0


def test_declining_prevents_starting_the_application(qapp, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    monkeypatch.setattr(single_instance_checker, "is_already_running", lambda: False)
    release = Mock()
    monkeypatch.setattr(single_instance_checker, "release", release)
    monkeypatch.setattr(privacy_notice, "ensure_mediapipe_consent", lambda settings: False)
    start = Mock(side_effect=AssertionError("Application should not start"))
    monkeypatch.setitem(sys.modules, "src.tray_app", SimpleNamespace(TrayApplication=start))
    assert main.main() == 0
    start.assert_not_called()
    release.assert_called_once()
