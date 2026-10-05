"""Exercise the real model and UI without changing the user's configuration."""
import argparse
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import tempfile
import time


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", action="store_true", help="also read the camera and restart the service")
    parser.add_argument("--report", type=Path, help="write a JSON result (also works in windowed EXEs)")
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    with tempfile.TemporaryDirectory(prefix="vcgca-smoke-") as home:
        os.environ["USERPROFILE"] = home
        os.environ["HOME"] = home
        opencv_variants = []
        for package in ("opencv-python", "opencv-contrib-python", "opencv-python-headless", "opencv-contrib-python-headless"):
            try:
                opencv_variants.append(f"{package}=={importlib.metadata.version(package)}")
            except importlib.metadata.PackageNotFoundError:
                pass
        if len(opencv_variants) != 1:
            raise RuntimeError(f"Expected one OpenCV distribution, found {opencv_variants}")
        print("PASS OpenCV distribution:", opencv_variants[0])
        modules = ["PyQt6.QtWidgets", "cv2", "numpy", "mediapipe", "pyautogui", "win32clipboard"]
        if not getattr(sys, "frozen", False):
            modules.append("PyInstaller")
        for module in modules:
            importlib.import_module(module)
            print(f"PASS import {module}")

        import numpy as np
        from src.tray_app import TrayApplication
        from src.core.gesture_service import gesture_service
        from mediapipe import Image, ImageFormat
        from src.utils.error_handler import error_handler
        from src.utils.version import get_version_string

        application = TrayApplication()
        gesture_service.disable_control()
        service_messages = []
        gesture_service.log_message.connect(service_messages.append)
        try:
            application.show_settings()
            application.create_hud_window()
            application.show_debug_window()
            application.show_log_window()
            application.app.processEvents()
            print("PASS settings, HUD, debug and log windows")

            if not gesture_service.initialize():
                raise RuntimeError(gesture_service.init_error or "Model initialization failed")
            frame = Image(image_format=ImageFormat.SRGB, data=np.zeros((64, 64, 3), dtype=np.uint8))
            gesture_service.recognizer.recognize_for_video(frame, 1)
            gesture_service.recognizer.recognize_for_video(frame, 2)
            print("PASS bundled model and video inference")

            if args.camera:
                for attempt in range(2):
                    if not gesture_service.initialize():
                        raise RuntimeError(gesture_service.init_error or "Model reinitialization failed")
                    gesture_service.start()
                    deadline = time.monotonic() + 8
                    first_frame_time = None
                    while gesture_service.isRunning() and time.monotonic() < deadline:
                        application.app.processEvents()
                        if gesture_service.frame_count:
                            if first_frame_time is None:
                                first_frame_time = time.monotonic()
                            elif time.monotonic() - first_frame_time >= 1:
                                break
                        time.sleep(0.02)
                    frame_count = gesture_service.frame_count
                    gesture_service.stop()
                    application.app.processEvents()
                    if not frame_count:
                        raise RuntimeError(gesture_service.init_error or "Camera did not produce frames")
                    if gesture_service.init_error:
                        raise RuntimeError(gesture_service.init_error)
                    inference_errors = [message for message in service_messages if "手势识别错误:" in message]
                    if inference_errors:
                        raise RuntimeError(inference_errors[0])
                    if gesture_service.cap is not None or gesture_service.recognizer is not None:
                        raise RuntimeError("Service did not release its resources")
                    print(f"PASS camera start/stop cycle {attempt + 1}: {frame_count} frames")
            else:
                gesture_service.stop()
        finally:
            gesture_service.stop()
            application.quit()
            application.app.processEvents()
            sys.excepthook = error_handler.original_excepthook
    print("All environment checks passed.")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps({
            "status": "passed", "version": get_version_string(),
            "frozen": bool(getattr(sys, "frozen", False)),
            "camera": args.camera, "checks": ["imports", "windows", "model"]
                + (["camera_start_stop_twice"] if args.camera else []),
        }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
