# 视觉手势控制系统 1.0.0

本版本将原 VCGCA-Lite 更名为「视觉手势控制系统 / Vision-Based Gesture Control System」，重新启用 1.0.0 版本号。为保留已有版本历史，本次 Git 标签为 `vision-v1.0.0`。

## 下载

- `VisionGestureControl-Setup-v1.0.0.exe`：Windows x64 安装程序。
- `VisionGestureControl-v1.0.0-windows-x64.zip`：便携版，解压完整目录后运行 `VisionGestureControl.exe`。
- `Qt-6.11.2-source-archives.zip`：本版本所用 Qt、PySide6 和 Shiboken 的上游源码归档。
- `SHA256SUMS.txt`：上述三个文件的 SHA-256 校验值。

程序需要 Windows 10/11 x64 和可供桌面应用访问的摄像头。改名版使用独立用户目录和安装标识，不会自动迁移或删除 VCGCA-Lite 的设置和截图。
如果覆盖安装此前的改名测试版，安装器会移除该测试版遗留的 PyQt6、可选音频库和 FFmpeg 插件；用户设置和截图不会被清理。

## 主要变化

- 统一中英文名称、图标、窗口标题和安装信息；保留摄像头手势识别、系统控制、HUD、设置和托盘功能。
- GUI 改用 PySide6 / Qt；显示桌面功能改用 Windows API，移除 PyQt6、PyAutoGUI 和 MouseInfo 的运行时依赖。
- 安装包和便携版均附有第三方许可证、版权声明、上游通知和源码获取方式。项目代码仍采用 MIT 许可证；Qt 和其他依赖适用各自的许可证。
- 根据 Google 的 MediaPipe Tasks 隐私说明，摄像头画面在本机处理，组件可能向 Google 发送 API 使用及性能指标。首次启动会在初始化识别服务前征求同意，可从托盘菜单撤回。

## 验证

- 39 项自动测试通过，覆盖设置、手势控制、窗口、Windows 快捷键及隐私选择。
- 源码版和打包版均通过依赖、窗口和内置模型检查；各自完成两轮真实摄像头启动、读取和停止检查。
- 已检查最终程序的多尺寸图标、第三方许可文件及打包内容。手势触发的各种动作未在所有硬件和光照条件下穷尽测试。

项目源码和详细的第三方声明见仓库的 `LICENSE` 和 `THIRD_PARTY_NOTICES.md`。
