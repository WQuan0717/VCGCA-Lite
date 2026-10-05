import sys

from src.utils.startup_manager import StartupManager


def test_source_startup_uses_the_environment_interpreter(monkeypatch):
    monkeypatch.setattr(sys, "executable", "C:/Program Files/Test Python/python.exe")
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    command = StartupManager.get_executable_path()
    assert command.startswith('"C:/Program Files/Test Python/python.exe" ')
    assert command.rstrip('"').endswith("main.py")


def test_packaged_startup_quotes_executable_path(monkeypatch):
    monkeypatch.setattr(sys, "executable", "C:/Program Files/VCGCA-Lite/VCGCA-Lite.exe")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert StartupManager.get_executable_path() == '"C:/Program Files/VCGCA-Lite/VCGCA-Lite.exe"'
