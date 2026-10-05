import pytest

from src.core.gesture_service import gesture_service
from src.windows.debug_window import DebugWindow
from src.windows.gesture_mapping_dialog import GestureMappingDialog


@pytest.mark.parametrize("prepare,response,valid", [
    ("None", "Closed_Fist", False),
    ("Open_Palm", "None", False),
    ("Open_Palm", "Open_Palm", False),
    ("Open_Palm", "Closed_Fist", True),
])
def test_only_usable_gesture_combinations_are_accepted(prepare, response, valid):
    dialog = GestureMappingDialog(prepare_gesture=prepare, response_gesture=response, action_key="screenshot")
    try:
        assert dialog.validate()[0] is valid
    finally:
        dialog.close()
        dialog.deleteLater()


def test_preview_subscribes_even_before_service_starts(monkeypatch):
    monkeypatch.setattr(gesture_service, "isRunning", lambda: False)
    gesture_service.disconnect_preview()
    window = DebugWindow()
    try:
        assert gesture_service.has_preview is True
    finally:
        window.close()
        window.deleteLater()
    assert gesture_service.has_preview is False
