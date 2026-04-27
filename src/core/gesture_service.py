import cv2
import numpy as np
import os
import time
from PyQt6.QtCore import QThread, pyqtSignal, QObject

# 导入MediaPipe - 使用Gesture Recognizer
try:
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core.base_options import BaseOptions
    from mediapipe import Image, ImageFormat
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError as e:
    MEDIAPIPE_AVAILABLE = False
    print(f"警告: MediaPipe导入失败: {e}")

from src.core.gesture_controller import gesture_controller
from src.utils.logger import log_manager


class GestureService(QThread):
    """手势识别服务 - 独立后台线程，不依赖UI"""
    frame_ready = pyqtSignal(np.ndarray)
    log_message = pyqtSignal(str)
    gesture_detected = pyqtSignal(str, float)  # 手势名称, 置信度
    control_state_changed = pyqtSignal(str)  # 控制状态变化
    init_progress = pyqtSignal(int, str)  # 进度百分比, 状态消息

    _instance = None
    _initialized = False

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(GestureService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if GestureService._initialized:
            return
        super().__init__()
        GestureService._initialized = True

        self.running = False
        self.frame_count = 0
        self.recognizer = None
        self.init_error = None
        self.cap = None

        # FPS计算相关
        self.fps = 0
        self.prev_time = 0

        # 手势识别结果缓存（避免重复输出）
        self.last_gestures = {}

        # 预览窗口连接状态
        self.has_preview = False

        # 控制功能启用状态
        self.control_enabled = True

        # 连接手势控制器的信号
        gesture_controller.log_message.connect(self._on_controller_log)
        gesture_controller.state_changed.connect(self._on_controller_state_changed)
        gesture_controller.action_triggered.connect(self._on_action_triggered)

    def _on_controller_log(self, message):
        """接收手势控制器的日志"""
        self.log_message.emit(f"[控制] {message}")

    def _on_controller_state_changed(self, state):
        """接收手势控制器的状态变化"""
        self.control_state_changed.emit(state)

    def _on_action_triggered(self, prepare, response):
        """接收动作触发信号"""
        self.log_message.emit(f"✓ 手势组合触发: {prepare} → {response}")

    def reload_settings(self):
        """重新加载设置（用于设置变更后实时应用）"""
        try:
            gesture_controller.reload_settings()
            self.log_message.emit("[配置] 手势设置已重新加载")
            return True
        except Exception as e:
            self.log_message.emit(f"[配置] 重新加载设置失败: {e}")
            return False

    def initialize(self, progress_callback=None):
        """初始化手势识别器
        
        Args:
            progress_callback: 进度回调函数，接收(进度百分比, 状态消息)
        """
        if not MEDIAPIPE_AVAILABLE:
            self.log_message.emit("MediaPipe不可用")
            if progress_callback:
                progress_callback(0, "MediaPipe不可用")
            return False

        try:
            # 步骤1: 检查模型文件 (10%)
            if progress_callback:
                progress_callback(10, "检查模型文件...")
            self.init_progress.emit(10, "检查模型文件...")
            
            model_path = self._get_model_path(progress_callback)
            if not model_path:
                return False

            # 步骤2: 创建Gesture Recognizer (60%)
            if progress_callback:
                progress_callback(60, "加载手势识别模型...")
            self.init_progress.emit(60, "加载手势识别模型...")
            
            base_options = BaseOptions(model_asset_path=model_path)
            options = vision.GestureRecognizerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                num_hands=2
            )
            self.recognizer = vision.GestureRecognizer.create_from_options(options)
            
            # 步骤3: 初始化完成 (80%)
            if progress_callback:
                progress_callback(80, "手势识别器初始化成功")
            self.init_progress.emit(80, "手势识别器初始化成功")
            
            self.log_message.emit("MediaPipe Gesture Recognizer初始化成功")
            return True
        except Exception as e:
            self.init_error = f"MediaPipe初始化失败: {e}"
            self.log_message.emit(self.init_error)
            if progress_callback:
                progress_callback(0, f"初始化失败: {e}")
            self.init_progress.emit(0, f"初始化失败: {e}")
            return False

    def _get_model_path(self, progress_callback=None):
        """获取或下载模型文件路径"""
        model_dir = os.path.join(os.path.expanduser("~"), ".vcgca-lite", "models")
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, "gesture_recognizer.task")

        if not os.path.exists(model_path):
            if progress_callback:
                progress_callback(20, "下载MediaPipe手势识别模型...")
            self.init_progress.emit(20, "下载MediaPipe手势识别模型...")
            self.log_message.emit("正在下载MediaPipe手势识别模型...")
            
            try:
                self._download_model(model_path, progress_callback)
            except Exception as e:
                self.init_error = f"模型下载失败: {e}"
                self.log_message.emit(self.init_error)
                if progress_callback:
                    progress_callback(0, f"模型下载失败: {e}")
                self.init_progress.emit(0, f"模型下载失败: {e}")
                return None

        return model_path

    def _download_model(self, model_path, progress_callback=None):
        """下载模型文件"""
        import urllib.request
        model_url = "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"

        try:
            # 使用自定义下载器显示进度
            def download_progress(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(int(downloaded * 100 / total_size), 100)
                    # 下载进度映射到 20-50%
                    mapped_progress = 20 + int(percent * 0.3)
                    if progress_callback:
                        progress_callback(mapped_progress, f"下载模型... {percent}%")
                    self.init_progress.emit(mapped_progress, f"下载模型... {percent}%")

            urllib.request.urlretrieve(model_url, model_path, reporthook=download_progress)
            self.log_message.emit(f"模型下载完成: {model_path}")
        except Exception as e:
            raise Exception(f"模型下载失败: {e}")

    def run(self):
        """主循环"""
        if self.init_error:
            self.log_message.emit(self.init_error)

        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.log_message.emit("错误：无法打开摄像头")
            return

        # 获取摄像头默认配置
        default_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        default_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        default_fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.log_message.emit(f"摄像头已启动")
        self.log_message.emit(f"默认分辨率: {default_width}x{default_height}")
        self.log_message.emit(f"默认帧率: {default_fps:.1f}fps")
        self.log_message.emit("手势控制功能已启用")

        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.log_message.emit("错误：无法读取摄像头画面")
                break

            # 水平翻转画面（镜像效果）
            frame = cv2.flip(frame, 1)

            # 手势识别
            if self.recognizer:
                frame = self.process_gestures(frame)

            # 手动触发控制器状态检查（确保冷静期等状态超时能被处理）
            gesture_controller.check_state_timeout()

            # 计算真实FPS
            current_time = time.time()
            if self.prev_time != 0:
                self.fps = 1 / (current_time - self.prev_time)
            self.prev_time = current_time

            # 添加帧计数和信息
            self.frame_count += 1
            fps_text = f"FPS: {self.fps:.1f}"
            cv2.putText(frame, fps_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # 显示控制状态
            if self.control_enabled:
                state_text = f"Control: {gesture_controller.get_current_state_display()}"
                cv2.putText(frame, state_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # 如果有预览窗口连接，发送帧
            if self.has_preview:
                self.frame_ready.emit(frame)

        # 释放资源
        if self.cap:
            self.cap.release()
        if self.recognizer:
            self.recognizer.close()

        self.log_message.emit("手势识别服务已停止")

    def process_gestures(self, frame):
        """处理手势识别"""
        try:
            # 转换颜色空间 BGR -> RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 创建MediaPipe Image
            mp_image = Image(image_format=ImageFormat.SRGB, data=rgb_frame)

            # 识别手势 (VIDEO模式需要使用recognize_for_video方法，并传入timestamp_ms)
            timestamp_ms = int(time.time() * 1000)
            recognition_result = self.recognizer.recognize_for_video(mp_image, timestamp_ms)

            # 处理识别结果
            if recognition_result.gestures:
                for idx, gestures in enumerate(recognition_result.gestures):
                    if gestures:
                        # 获取最高置信度的手势
                        top_gesture = gestures[0]
                        gesture_name = top_gesture.category_name
                        confidence = top_gesture.score

                        # 只在手势变化时输出日志
                        hand_key = f"hand_{idx}"
                        if hand_key not in self.last_gestures or \
                           self.last_gestures[hand_key] != gesture_name:
                            self.last_gestures[hand_key] = gesture_name
                            self.log_message.emit(f"手势识别: {gesture_name} (置信度: {confidence:.2f})")
                            self.gesture_detected.emit(gesture_name, confidence)

                            # 传递给手势控制器进行处理
                            if self.control_enabled:
                                gesture_controller.on_gesture_detected(gesture_name, idx)

                        # 在画面上显示手势名称
                        if recognition_result.hand_landmarks:
                            hand_landmarks = recognition_result.hand_landmarks[idx]
                            wrist = hand_landmarks[0]  # 手腕位置
                            h, w = frame.shape[:2]
                            cx, cy = int(wrist.x * w), int(wrist.y * h)

                            # 显示手势名称
                            label = f"{gesture_name}: {confidence:.2f}"
                            cv2.putText(frame, label,
                                       (cx - 50, cy - 20),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                        # 绘制手部关键点
                        if recognition_result.hand_landmarks:
                            self._draw_landmarks(frame, recognition_result.hand_landmarks[idx])

            else:
                # 没有检测到手（手离开画面），发送None作为丢失目标信号
                if self.last_gestures:
                    # 通知控制器手已离开
                    if self.control_enabled:
                        for hand_key in list(self.last_gestures.keys()):
                            gesture_controller.on_gesture_detected("None", int(hand_key.split("_")[1]))
                    self.log_message.emit("手势识别: None (丢失目标)")
                    self.last_gestures.clear()

        except Exception as e:
            self.log_message.emit(f"手势识别错误: {e}")

        return frame

    def _draw_landmarks(self, frame, landmarks):
        """绘制手部关键点"""
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # 拇指
            (0, 5), (5, 6), (6, 7), (7, 8),  # 食指
            (0, 9), (9, 10), (10, 11), (11, 12),  # 中指
            (0, 13), (13, 14), (14, 15), (15, 16),  # 无名指
            (0, 17), (17, 18), (18, 19), (19, 20),  # 小指
            (0, 5), (5, 9), (9, 13), (13, 17)  # 手掌
        ]

        h, w = frame.shape[:2]

        # 绘制关键点
        for landmark in landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)

        # 绘制连接线
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start_point = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
                end_point = (int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h))
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)

    def stop(self):
        """停止服务"""
        self.running = False
        self.wait()

    def connect_preview(self):
        """连接预览窗口"""
        self.has_preview = True

    def disconnect_preview(self):
        """断开预览窗口"""
        self.has_preview = False

    def clear_gesture_cache(self):
        """清空手势缓存，用于冷静期结束后重新开始检测"""
        self.last_gestures.clear()

    def enable_control(self):
        """启用控制功能"""
        self.control_enabled = True
        gesture_controller.reload_settings()
        self.log_message.emit("手势控制功能已启用")

    def disable_control(self):
        """禁用控制功能"""
        self.control_enabled = False
        self.log_message.emit("手势控制功能已禁用")


# 全局手势识别服务实例
gesture_service = GestureService()
