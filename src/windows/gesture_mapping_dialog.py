from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QGridLayout)
from PyQt6.QtCore import Qt

from src.core.system_control import SystemController
from src.utils.gesture_names import (
    get_gesture_display_name, get_gesture_english_name,
    get_all_gesture_display_names
)


class GestureMappingDialog(QDialog):
    """手势映射编辑对话框"""

    def __init__(self, parent=None, prepare_gesture="", response_gesture="", action_key=""):
        super().__init__(parent)
        self.setWindowTitle("编辑手势映射" if prepare_gesture else "添加手势映射")
        self.setMinimumSize(350, 200)

        # 保存初始值（用于判断是添加还是编辑）
        self._initial_prepare = prepare_gesture
        self._initial_response = response_gesture
        self._initial_action_key = action_key

        self.init_ui()

        # 如果有初始值，设置为编辑模式
        if prepare_gesture:
            # 将英文名称转换为中文显示
            display_name = get_gesture_display_name(prepare_gesture)
            self.prepare_combo.setCurrentText(display_name)
        if response_gesture:
            display_name = get_gesture_display_name(response_gesture)
            self.response_combo.setCurrentText(display_name)
        if action_key:
            # 将action_key转换为显示名称
            action_display = SystemController.get_action_display_name(action_key)
            index = self.action_combo.findText(action_display)
            if index >= 0:
                self.action_combo.setCurrentIndex(index)

    def init_ui(self):
        layout = QVBoxLayout()

        # 表单布局
        form_layout = QGridLayout()

        # 准备手势（显示中文）
        form_layout.addWidget(QLabel("准备手势:"), 0, 0)
        self.prepare_combo = QComboBox()
        # 使用中文手势名称
        self.prepare_combo.addItems(get_all_gesture_display_names())
        form_layout.addWidget(self.prepare_combo, 0, 1)

        # 响应手势（显示中文）
        form_layout.addWidget(QLabel("响应手势:"), 1, 0)
        self.response_combo = QComboBox()
        # 使用中文手势名称
        self.response_combo.addItems(get_all_gesture_display_names())
        form_layout.addWidget(self.response_combo, 1, 1)

        # 控制功能（下拉列表显示中文，存储英文key）
        form_layout.addWidget(QLabel("控制功能:"), 2, 0)
        self.action_combo = QComboBox()
        # 从SystemController获取所有显示名称（中文）
        for key in SystemController.get_all_action_keys():
            self.action_combo.addItem(SystemController.get_action_display_name(key), key)
        form_layout.addWidget(self.action_combo, 2, 1)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_btn = QPushButton("确定")
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 20px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.ok_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 5px 20px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_data(self):
        """获取对话框中的数据"""
        # 将中文手势名称转换回英文
        prepare_display = self.prepare_combo.currentText()
        response_display = self.response_combo.currentText()
        # 获取选中的action_key（存储在itemData中）
        action_key = self.action_combo.currentData()

        return {
            "prepare": get_gesture_english_name(prepare_display),
            "response": get_gesture_english_name(response_display),
            "action": action_key  # 直接返回英文key
        }

    def validate(self):
        """验证输入数据"""
        data = self.get_data()
        if data["prepare"] == "None" and data["response"] == "None":
            return False, "准备手势和响应手势不能同时为None"
        return True, ""

    def accept(self):
        """确认按钮点击"""
        valid, message = self.validate()
        if valid:
            super().accept()
        else:
            # 可以在这里显示错误提示
            pass
