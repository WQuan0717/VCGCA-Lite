import ctypes
from types import SimpleNamespace

import pytest

from src.core.system_control import SystemController, _Input


class FakeSendInput:
    def __init__(self, first_result):
        self.first_result = first_result
        self.calls = []

    def __call__(self, count, inputs, item_size):
        self.calls.append(([(entry.keyboard.vk, entry.keyboard.flags)
                            for entry in inputs[:count]], item_size))
        return self.first_result if len(self.calls) == 1 else count


def test_show_desktop_sends_win_d_and_releases_both_keys(monkeypatch):
    sender = FakeSendInput(4)
    monkeypatch.setattr(ctypes, "WinDLL", lambda *a, **kw: SimpleNamespace(SendInput=sender))
    SystemController.show_desktop(None)
    assert sender.calls == [([(0x5B, 0), (0x44, 0), (0x44, 2), (0x5B, 2)],
                             ctypes.sizeof(_Input))]
    if ctypes.sizeof(ctypes.c_void_p) == 8:
        assert ctypes.sizeof(_Input) == 40


def test_partial_shortcut_releases_pressed_keys_and_reports_failure(monkeypatch):
    sender = FakeSendInput(2)
    monkeypatch.setattr(ctypes, "WinDLL", lambda *a, **kw: SimpleNamespace(SendInput=sender))
    with pytest.raises(OSError, match="未能完整发送"):
        SystemController.show_desktop(None)
    assert sender.calls[1][0] == [(0x44, 2), (0x5B, 2)]
