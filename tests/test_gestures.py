from types import SimpleNamespace
from unittest.mock import Mock
import importlib
import threading
import time

import numpy as np
import pytest

controller_module = importlib.import_module("src.core.gesture_controller")
service_module = importlib.import_module("src.core.gesture_service")


@pytest.fixture
def clock(monkeypatch):
    now = [10.0]
    monkeypatch.setattr(controller_module, "time", SimpleNamespace(
        time=lambda: now[0], monotonic=lambda: now[0], sleep=lambda _: None))
    return now


@pytest.fixture
def controller(clock, monkeypatch):
    instance = controller_module.GestureController()
    monkeypatch.setattr(instance, "_execute_action", Mock())
    return instance


def test_second_hand_cannot_complete_first_hands_sequence(controller, clock):
    controller.on_gesture_detected("Open_Palm", "Left")
    clock[0] += 1.1
    controller.check_state_timeout()
    controller.on_gesture_detected("Closed_Fist", "Right")
    controller._execute_action.assert_not_called()
    controller.on_gesture_detected("Closed_Fist", "Left")
    controller._execute_action.assert_called_once_with("Open_Palm", "Closed_Fist")


def test_second_hand_cannot_interrupt_preparation(controller):
    controller.on_gesture_detected("Open_Palm", "Left")
    controller.on_gesture_detected("Victory", "Right")
    assert controller.prepare_gesture == "Open_Palm"


def test_response_after_loss_timeout_does_not_execute(controller, clock):
    controller.on_gesture_detected("Open_Palm", "Left")
    clock[0] += 1.1
    controller.check_state_timeout()
    controller.on_gesture_detected("None", "Left")
    clock[0] += 1.1
    controller.on_gesture_detected("Closed_Fist", "Left")
    controller._execute_action.assert_not_called()
    assert controller.current_state == controller.STATE_IDLE


def result(*hands):
    return SimpleNamespace(
        gestures=[[SimpleNamespace(category_name=gesture, score=0.95)]
                  for handedness, gesture in hands],
        handedness=[[SimpleNamespace(category_name=handedness)]
                    for handedness, gesture in hands],
        hand_landmarks=[])


@pytest.fixture
def service(monkeypatch):
    service = service_module.gesture_service
    service.last_gestures.clear()
    service.control_enabled = True
    service.recognizer = Mock()
    yield service
    service.recognizer = None
    service.last_gestures.clear()


def test_disappearing_hand_is_reported_while_other_hand_remains(service, monkeypatch):
    detected = Mock()
    monkeypatch.setattr(service_module.gesture_controller, "on_gesture_detected", detected)
    service.recognizer.recognize_for_video.side_effect = [
        result(("Left", "Open_Palm"), ("Right", "Victory")),
        result(("Right", "Victory"))]
    frame = np.zeros((16, 16, 3), dtype=np.uint8)
    service.process_gestures(frame)
    detected.reset_mock()
    service.process_gestures(frame)
    detected.assert_any_call("None", "Left")
    assert "Left" not in service.last_gestures


def test_video_timestamps_always_increase(service, monkeypatch):
    monkeypatch.setattr(service_module, "time", SimpleNamespace(
        time=lambda: 10.0, monotonic=lambda: 10.0))
    service.recognizer.recognize_for_video.return_value = result()
    frame = np.zeros((16, 16, 3), dtype=np.uint8)
    service.process_gestures(frame)
    service.process_gestures(frame)
    calls = service.recognizer.recognize_for_video.call_args_list
    assert len(calls) == 2
    assert calls[1].args[1] > calls[0].args[1]


@pytest.mark.parametrize("opened,raises", [(False, False), (True, True)])
def test_camera_failure_releases_every_resource(service, monkeypatch, opened, raises):
    cap = Mock()
    cap.isOpened.return_value = opened
    cap.get.return_value = 30
    cap.read.side_effect = RuntimeError("camera disconnected") if raises else [(False, None)]
    recognizer = service.recognizer
    fallback = Mock()
    fallback.isOpened.return_value = False
    capture = Mock(side_effect=[cap, fallback])
    monkeypatch.setattr(service_module.cv2, "VideoCapture", capture)
    service.run()
    cap.release.assert_called_once()
    if not opened:
        fallback.release.assert_called_once()
    recognizer.close.assert_called_once()
    assert service.running is False
    assert service.cap is None
    assert service.recognizer is None


def test_reinitialization_closes_old_model_and_resets_session(service, monkeypatch):
    old_model = service.recognizer
    new_model = Mock()
    service.last_gestures["Left"] = "Open_Palm"
    service.init_error = "previous initialization failed"
    service.frame_count = 12
    monkeypatch.setattr(service, "_get_model_path", lambda _: "unused.task")
    monkeypatch.setattr(service_module.vision.GestureRecognizer, "create_from_options", lambda _: new_model)
    assert service.initialize() is True
    old_model.close.assert_called_once()
    assert service.init_error is None
    assert service.last_gestures == {}
    assert service.frame_count == 0
    assert service.recognizer is new_model


def test_disabling_control_cancels_pending_sequence(service):
    controller = service_module.gesture_controller
    controller.on_gesture_detected("Open_Palm", "Left")
    try:
        service.disable_control()
        assert controller.current_state == controller.STATE_IDLE
        service.enable_control()
        assert controller.current_state == controller.STATE_IDLE
    finally:
        controller._reset_to_idle()


def test_changing_result_order_does_not_create_new_gestures(service, monkeypatch):
    detected = Mock()
    monkeypatch.setattr(service_module.gesture_controller, "on_gesture_detected", detected)
    service.recognizer.recognize_for_video.side_effect = [
        result(("Left", "Open_Palm"), ("Right", "Victory")),
        result(("Right", "Victory"), ("Left", "Open_Palm"))]
    frame = np.zeros((16, 16, 3), dtype=np.uint8)
    service.process_gestures(frame)
    detected.reset_mock()
    service.process_gestures(frame)
    detected.assert_not_called()


def test_stop_during_camera_open_does_not_start_capturing(service, monkeypatch):
    camera_opening = threading.Event()
    finish_opening = threading.Event()
    cap = Mock()

    def is_opened():
        camera_opening.set()
        finish_opening.wait(2)
        return True

    cap.isOpened.side_effect = is_opened
    cap.get.return_value = 30
    cap.read.return_value = (False, None)
    monkeypatch.setattr(service_module.cv2, "VideoCapture", lambda *args: cap)
    service.start()
    stopper = threading.Thread(target=service.stop, daemon=True)
    try:
        assert camera_opening.wait(2)
        stopper.start()
        deadline = time.monotonic() + 2
        while not service.isInterruptionRequested() and time.monotonic() < deadline:
            time.sleep(0.005)
        finish_opening.set()
        stopper.join(3)
        assert not stopper.is_alive()
        cap.read.assert_not_called()
        assert not service.isRunning()
    finally:
        finish_opening.set()
        service.stop()


def test_full_sequence_can_repeat_after_cooldown(service, clock, monkeypatch):
    controller = service_module.gesture_controller
    controller.reload_settings()
    execute = Mock()
    monkeypatch.setattr(controller, "_execute_action", execute)
    frame = np.zeros((16, 16, 3), dtype=np.uint8)
    try:
        for attempt in range(2):
            service.recognizer.recognize_for_video.return_value = result(("Left", "Open_Palm"))
            service.process_gestures(frame)
            assert controller.current_state == controller.STATE_WAITING_PREPARE
            clock[0] += 1.1
            controller.check_state_timeout()
            service.recognizer.recognize_for_video.return_value = result(("Left", "Closed_Fist"))
            service.process_gestures(frame)
            assert controller.current_state == controller.STATE_COOLDOWN
            clock[0] += 2.1
            controller.check_state_timeout()
            assert controller.current_state == controller.STATE_IDLE
        assert execute.call_count == 2
        execute.assert_called_with("Open_Palm", "Closed_Fist")
    finally:
        controller._reset_to_idle()


def test_windows_camera_prefers_directshow(service, monkeypatch):
    monkeypatch.setattr(service_module.sys, "platform", "win32")
    cap = Mock()
    cap.isOpened.return_value = True
    cap.get.return_value = 30
    cap.read.return_value = (False, None)
    capture = Mock(return_value=cap)
    monkeypatch.setattr(service_module.cv2, "VideoCapture", capture)
    service.run()
    capture.assert_called_once_with(0, service_module.cv2.CAP_DSHOW)
    cap.release.assert_called_once()


def test_failed_directshow_camera_is_released_before_fallback(service, monkeypatch):
    monkeypatch.setattr(service_module.sys, "platform", "win32")
    preferred, fallback = Mock(), Mock()
    preferred.isOpened.return_value = False
    fallback.isOpened.return_value = True
    fallback.get.return_value = 30
    fallback.read.return_value = (False, None)

    def capture(index, backend=None):
        if backend == service_module.cv2.CAP_DSHOW:
            return preferred
        preferred.release.assert_called_once()
        return fallback

    monkeypatch.setattr(service_module.cv2, "VideoCapture", capture)
    service.run()
    preferred.release.assert_called_once()
    fallback.release.assert_called_once()
