"""
手势控制器 - 根据伪代码逻辑重构
核心逻辑：
1. 检测准备手势 → 进入准备等待状态
2. 在准备时间内持续检测，如果手势变化则重置
3. 准备时间结束 → 进入变化等待状态
4. 在变化等待状态：
   - 如果检测到 None，开始/继续变化时间计时
   - 如果在计时期间检测到响应手势，立即停止计时并判定
   - 如果变化时间结束还没检测到手势，重置到空闲
   - 如果检测到响应手势，立即检查映射
   - 如果映射存在，执行动作 → 进入冷静期
   - 如果映射不存在，重置到空闲
"""

import time
from PyQt6.QtCore import QObject, pyqtSignal

from src.core.system_control import system_controller
from src.utils.settings_manager import settings_manager


class GestureController(QObject):
    """手势控制器 - 管理手势序列检测和控制功能执行"""

    # 信号
    state_changed = pyqtSignal(str)  # 状态变化信号
    action_triggered = pyqtSignal(str, str)  # 动作触发信号 (准备手势, 响应手势)
    log_message = pyqtSignal(str)  # 日志消息
    screenshot_start = pyqtSignal()  # 截图开始信号（通知HUD隐藏）
    screenshot_end = pyqtSignal(bool, str)  # 截图结束信号（成功/失败, 消息）

    def __init__(self):
        super().__init__()

        # 状态定义
        self.STATE_IDLE = "idle"           # 空闲状态 - 等待准备手势
        self.STATE_WAITING_PREPARE = "waiting_prepare"  # 准备等待期
        self.STATE_WAITING_RESPONSE = "waiting_response"  # 变化等待期（滑动窗口）
        self.STATE_COOLDOWN = "cooldown"   # 冷静期

        self.current_state = self.STATE_IDLE

        # 时间相关（秒）
        self.prepare_time = 1.0   # 准备时间
        self.change_time = 1.0    # 变化时间
        self.cooldown_time = 2.0  # 冷静时间

        # 当前检测到的手势
        self.prepare_gesture = None  # 准备手势

        # 时间记录
        self.state_start_time = 0  # 当前状态开始时间
        self.none_start_time = 0   # None状态开始时间（用于变化等待期）
        self.is_timing = False     # 是否在计时（变化等待期）

        # 加载设置
        self.load_settings()

    def load_settings(self):
        """从设置加载配置"""
        from src.core.system_control import SystemController

        gesture_settings = settings_manager.get_section("gesture")

        # 默认配置
        default_settings = {
            "prepare_time": 1000,
            "change_time": 1000,
            "cooldown_time": 2000,
            "mappings": [
                {"prepare": "Open_Palm", "response": "Closed_Fist", "action": "screenshot"},
                {"prepare": "Open_Palm", "response": "Thumb_Up", "action": "volume_up"},
                {"prepare": "Open_Palm", "response": "Thumb_Down", "action": "volume_down"},
                {"prepare": "Victory", "response": "Pointing_Up", "action": "show_desktop"}
            ]
        }

        # 如果配置为空或无效，使用默认配置
        if not gesture_settings:
            gesture_settings = default_settings
            settings_manager.set_section("gesture", gesture_settings)
            settings_manager.save_settings()
            self.log_message.emit("[配置] 使用默认手势配置")

        # 时间设置（毫秒转秒）
        self.prepare_time = gesture_settings.get("prepare_time", 1000) / 1000.0
        self.change_time = gesture_settings.get("change_time", 1000) / 1000.0
        self.cooldown_time = gesture_settings.get("cooldown_time", 2000) / 1000.0

        # 加载手势映射 - 强制使用英文key
        mappings = gesture_settings.get("mappings", [])
        valid_mappings = []

        for mapping in mappings:
            action = mapping.get("action", "")
            # 只接受英文key
            if action in SystemController.AVAILABLE_ACTIONS:
                valid_mappings.append(mapping)

        # 如果没有有效映射，使用默认映射
        if not valid_mappings:
            valid_mappings = default_settings["mappings"]
            gesture_settings["mappings"] = valid_mappings
            settings_manager.set_section("gesture", gesture_settings)
            settings_manager.save_settings()
            self.log_message.emit("[配置] 配置无效，已重置为默认配置")

        self.mappings = valid_mappings

        self.log_message.emit(f"[配置] 准备时间={self.prepare_time}s | 变化时间={self.change_time}s | 冷静时间={self.cooldown_time}s | 映射数={len(self.mappings)}")

    def reload_settings(self):
        """重新加载设置"""
        self.load_settings()

    def on_gesture_detected(self, gesture_name, hand_id=0):
        """当检测到新手势时调用 - 根据伪代码逻辑重构"""
        current_time = time.time()

        # 冷静期检查 - 如果冷静期结束，自动切换到空闲
        if self.current_state == self.STATE_COOLDOWN:
            if current_time - self.state_start_time >= self.cooldown_time:
                self._reset_to_idle("冷静期结束")
                self.log_message.emit("[状态] 冷静期结束 → 空闲")
            else:
                # 冷静期内忽略所有手势
                return

        # 空闲状态：等待准备手势
        if self.current_state == self.STATE_IDLE:
            if self._is_valid_prepare_gesture(gesture_name):
                # 检测到有效准备手势，进入准备等待期
                self.prepare_gesture = gesture_name
                self.current_state = self.STATE_WAITING_PREPARE
                self.state_start_time = current_time
                self.state_changed.emit("waiting_prepare")
                self.log_message.emit(f"[状态] 空闲 → 准备等待 | 手势: {gesture_name} | 需保持 {self.prepare_time}s")

        # 准备等待期：检查手势是否保持
        elif self.current_state == self.STATE_WAITING_PREPARE:
            elapsed = current_time - self.state_start_time

            if elapsed >= self.prepare_time:
                # 准备时间已达到，进入变化等待期
                self.current_state = self.STATE_WAITING_RESPONSE
                self.state_start_time = current_time
                self.is_timing = False  # 重置计时状态
                self.none_start_time = 0
                self.state_changed.emit("waiting_response")
                self.log_message.emit(f"[状态] 准备等待 → 变化等待 | 准备手势: {self.prepare_gesture} 已确认")
                # 立即处理当前手势作为响应手势
                self._process_response_gesture(gesture_name, current_time)
            elif gesture_name != self.prepare_gesture and gesture_name != "None":
                # 准备时间未达到，且手势变成其他非None手势，重置
                self.log_message.emit(f"[准备] 手势变化 {self.prepare_gesture} → {gesture_name}，重新检测")
                self._reset_to_idle("")
                # 如果新手势也是有效的准备手势，重新开始
                if self._is_valid_prepare_gesture(gesture_name):
                    self.prepare_gesture = gesture_name
                    self.current_state = self.STATE_WAITING_PREPARE
                    self.state_start_time = current_time
                    self.state_changed.emit("waiting_prepare")
                    self.log_message.emit(f"[状态] 空闲 → 准备等待 | 手势: {gesture_name} | 需保持 {self.prepare_time}s")
            # 如果是None或保持原手势，继续等待（不输出日志避免刷屏）

        # 变化等待期：等待响应手势
        elif self.current_state == self.STATE_WAITING_RESPONSE:
            if gesture_name == "None":
                # 检测到None，开始/继续计时
                if not self.is_timing:
                    self.is_timing = True
                    self.none_start_time = current_time
                    self.log_message.emit(f"[变化] 检测到None，开始 {self.change_time}s 计时...")
                else:
                    # 检查是否超时
                    elapsed = current_time - self.none_start_time
                    remaining = self.change_time - elapsed
                    if elapsed >= self.change_time:
                        # 变化时间结束，重置到空闲
                        self.log_message.emit(f"[变化] 计时结束，未检测到手势")
                        self._reset_to_idle("变化时间结束")
                    elif int(elapsed * 10) % 5 == 0:  # 每0.5秒输出一次倒计时
                        self.log_message.emit(f"[变化] 等待中... {remaining:.1f}s")
                return
            elif gesture_name == self.prepare_gesture:
                # 仍然是准备手势，停止计时（如果有）
                if self.is_timing:
                    self.is_timing = False
                    self.log_message.emit(f"[变化] 回到准备手势，停止计时")
                return
            else:
                # 变成了其他手势，停止计时并立即判定
                self.is_timing = False
                # 检查是否是有效的响应手势
                if self._is_valid_response_gesture(gesture_name, self.prepare_gesture):
                    # 有效的响应手势，执行功能
                    self.log_message.emit(f"[变化] 检测到响应手势: {gesture_name}")
                    self._execute_action(self.prepare_gesture, gesture_name)
                    # 进入冷静期
                    self.current_state = self.STATE_COOLDOWN
                    self.state_start_time = current_time
                    self.state_changed.emit("cooldown")
                    self.log_message.emit(f"[状态] 变化等待 → 冷静期 | 时长: {self.cooldown_time}s")
                else:
                    # 无效的响应手势，放弃
                    self.log_message.emit(f"[变化] 无效手势: {gesture_name}，放弃")
                    self._reset_to_idle("")

    def _is_valid_prepare_gesture(self, gesture_name):
        """检查是否是有效的准备手势"""
        if gesture_name == "None":
            return False
        if not self.mappings:
            return False
        for mapping in self.mappings:
            if mapping.get("prepare") == gesture_name:
                return True
        return False

    def _is_valid_response_gesture(self, gesture_name, prepare_gesture):
        """检查是否是有效的响应手势"""
        if gesture_name == "None":
            return False
        if not self.mappings:
            return False
        for mapping in self.mappings:
            if mapping.get("prepare") == prepare_gesture and mapping.get("response") == gesture_name:
                return True
        return False

    def _get_action_for_gestures(self, prepare_gesture, response_gesture):
        """获取手势组合对应的控制功能"""
        if not self.mappings:
            return None
        for mapping in self.mappings:
            if (mapping.get("prepare") == prepare_gesture and
                mapping.get("response") == response_gesture):
                return mapping.get("action")
        return None

    def _execute_action(self, prepare_gesture, response_gesture):
        """执行控制功能"""
        action_key = self._get_action_for_gestures(prepare_gesture, response_gesture)
        if action_key:
            self.action_triggered.emit(prepare_gesture, response_gesture)

            # 如果是截图功能，先发射信号让 HUD 隐藏
            if action_key == "screenshot":
                self.screenshot_start.emit()
                # 给 HUD 一点时间隐藏（100ms）
                import time
                time.sleep(0.1)

            success, message = system_controller.execute_action(action_key)

            # 如果是截图功能，发射结束信号
            if action_key == "screenshot":
                self.screenshot_end.emit(success, message)

            if success:
                self.log_message.emit(f"[动作] ✓ {message}")
            else:
                self.log_message.emit(f"[动作] ✗ {message}")
        else:
            self.log_message.emit(f"[动作] 未找到映射: {prepare_gesture} → {response_gesture}")

    def _reset_to_idle(self, reason=""):
        """重置到空闲状态"""
        old_state = self.current_state
        self.current_state = self.STATE_IDLE
        self.prepare_gesture = None
        self.is_timing = False
        self.none_start_time = 0
        self.state_changed.emit("idle")
        if reason:
            self.log_message.emit(f"[状态] {old_state} → 空闲 | 原因: {reason}")
        else:
            self.log_message.emit(f"[状态] {old_state} → 空闲")

    def _process_response_gesture(self, gesture_name, current_time):
        """处理响应手势（刚进入变化等待期时调用）"""
        if gesture_name == "None":
            # None手势，开始计时
            self.is_timing = True
            self.none_start_time = current_time
            self.log_message.emit(f"[变化] 进入变化等待期，当前None，开始 {self.change_time}s 计时...")
            return
        elif gesture_name == self.prepare_gesture:
            # 仍然是准备手势，不开始计时
            self.is_timing = False
            self.log_message.emit(f"[变化] 进入变化等待期，保持准备手势，等待变化...")
            return
        else:
            # 变成了其他手势，立即判定
            self.is_timing = False
            # 检查是否是有效的响应手势
            if self._is_valid_response_gesture(gesture_name, self.prepare_gesture):
                # 有效的响应手势，执行功能
                self.log_message.emit(f"[变化] 检测到响应手势: {gesture_name}")
                self._execute_action(self.prepare_gesture, gesture_name)
                # 进入冷静期
                self.current_state = self.STATE_COOLDOWN
                self.state_start_time = current_time
                self.state_changed.emit("cooldown")
                self.log_message.emit(f"[状态] 变化等待 → 冷静期 | 时长: {self.cooldown_time}s")
            else:
                # 无效的响应手势，放弃
                self.log_message.emit(f"[变化] 无效手势: {gesture_name}，放弃")
                self._reset_to_idle("")

    def check_state_timeout(self):
        """检查状态超时（由 gesture_service 定期调用）"""
        current_time = time.time()

        if self.current_state == self.STATE_WAITING_PREPARE:
            # 准备时间结束，进入变化等待期
            if current_time - self.state_start_time >= self.prepare_time:
                self.current_state = self.STATE_WAITING_RESPONSE
                self.state_start_time = current_time
                self.is_timing = False
                self.none_start_time = 0
                self.state_changed.emit("waiting_response")
                self.log_message.emit(f"[状态] 准备等待 → 变化等待 | 准备手势: {self.prepare_gesture} 已确认")

        elif self.current_state == self.STATE_WAITING_RESPONSE:
            # 如果在计时，检查是否超时
            if self.is_timing:
                elapsed = current_time - self.none_start_time
                if elapsed >= self.change_time:
                    self.log_message.emit(f"[变化] 计时结束，未检测到手势")
                    self._reset_to_idle("变化时间结束")

        elif self.current_state == self.STATE_COOLDOWN:
            # 冷静期结束，重置到空闲
            if current_time - self.state_start_time >= self.cooldown_time:
                # 清空手势缓存，确保即使用户保持相同手势也能触发新识别
                from src.core.gesture_service import gesture_service
                gesture_service.clear_gesture_cache()

                self._reset_to_idle("冷静期结束")
                self.log_message.emit("[状态] 冷静期结束 → 空闲")

    def get_current_state_display(self):
        """获取当前状态的显示文本（用于OpenCV显示，使用英文避免编码问题）"""
        state_map = {
            self.STATE_IDLE: "IDLE",
            self.STATE_WAITING_PREPARE: "PREPARE",
            self.STATE_WAITING_RESPONSE: "RESPONSE",
            self.STATE_COOLDOWN: "COOLDOWN",
        }
        return state_map.get(self.current_state, "UNKNOWN")


# 全局手势控制器实例
gesture_controller = GestureController()
