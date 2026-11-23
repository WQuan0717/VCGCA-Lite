from pathlib import Path

from PIL import Image
from PySide6.QtWidgets import QLabel, QTextBrowser

from src.core.system_control import SystemController
from src.utils.version import APP_ENGLISH_NAME, APP_EXECUTABLE_NAME, APP_NAME
from src.windows.debug_window import DebugWindow
from src.windows.hud_window import HUDWindow
from src.windows.log_window import LogWindow
from src.windows.settings_window import SettingsWindow
from src.windows.splash_window import SplashWindow


def test_real_windows_show_consistent_new_name(qapp):
    windows = [SplashWindow(), HUDWindow(), DebugWindow(), LogWindow(), SettingsWindow()]
    try:
        assert all(APP_NAME in window.windowTitle() for window in windows)
        labels = [label.text() for window in windows for label in window.findChildren(QLabel)]
        assert APP_ENGLISH_NAME in labels
        assert any("The Qt Company Ltd." in text and "LGPL" in text
                   and "third_party/licenses/qt/qtbase/LICENSES/" in text for text in labels)
        help_text = " ".join(browser.toPlainText() for browser in windows[-1].findChildren(QTextBrowser))
        assert f"{APP_EXECUTABLE_NAME}.exe" in help_text
        assert "VCGCA-Lite" not in help_text
    finally:
        for window in windows:
            window.close()
            window.deleteLater()
        qapp.processEvents()


def test_new_screenshot_directory_does_not_change_old_files(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    pictures = tmp_path / "Pictures"
    current = pictures / "VisionGestureControl-Screenshots"
    legacy = pictures / "VCGCA-Screenshots"
    assert SystemController.get_default_screenshot_dir() == current
    legacy.mkdir(parents=True)
    (legacy / "existing.png").write_bytes(b"previous screenshot")
    assert SystemController.get_default_screenshot_dir() == current
    current.mkdir()
    assert SystemController.get_default_screenshot_dir() == current
    assert (legacy / "existing.png").read_bytes() == b"previous screenshot"


def test_icon_contains_common_windows_sizes():
    icon = Image.open(Path(__file__).resolve().parents[1] / "assets" / "app.ico")
    assert {(16, 16), (24, 24), (32, 32), (48, 48), (256, 256)} <= icon.ico.sizes()
