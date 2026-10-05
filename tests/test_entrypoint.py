import json
from types import SimpleNamespace
from unittest.mock import Mock
import sys

import pytest
from PyQt6.QtCore import QTimer

import main as entrypoint
from src.tray_app import TrayApplication, QSystemTrayIcon


def test_diagnostic_failure_returns_nonzero_and_writes_report(tmp_path, monkeypatch):
    report = tmp_path / "result.json"
    monkeypatch.setattr(sys, "argv", ["main.py", "--check-environment", "--report", str(report)])

    def fail_check():
        raise RuntimeError("dependency unavailable")

    monkeypatch.setitem(sys.modules, "scripts.check_environment", SimpleNamespace(main=fail_check))
    assert entrypoint.main() == 1
    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["status"] == "failed"
    assert result["error"] == "dependency unavailable"


def test_settings_shortcut_opens_settings_in_event_loop(qapp, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--settings"])
    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", lambda: True)
    qapp.setQuitOnLastWindowClosed(False)
    application = SimpleNamespace(app=qapp, show_splash_and_run=Mock(), show_settings=Mock())
    QTimer.singleShot(50, qapp.quit)
    with pytest.raises(SystemExit) as stopped:
        TrayApplication.run(application)
    assert stopped.value.code == 0
    application.show_settings.assert_called_once()
