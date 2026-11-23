# 第三方组件、许可证及源码

本文件适用于视觉手势控制系统 1.0.0 的 Windows x64 发行包。项目自行编写的代码采用根目录的 MIT 许可证；第三方组件、模型和安装器翻译继续适用各自的许可证。许可证原文、版权声明和上游提供的通知位于 `third_party/licenses/`；Python 组件版本和随包元数据见 `third_party/python-components.json`。许可证文件的收录范围包含一些上游包中的备用文本，并不表示所有列出的可选组件均在程序中运行。

## Qt for Python 和 Qt

- 本版本使用 **PySide6-Essentials 6.11.2**、**Shiboken 6.11.2** 和 **Qt 6.11.2**。我们选择适用的 GNU LGPL 3.0 条款；原文和 Qt 上游组件声明在 `third_party/licenses/qt/`。Qt 和 Qt for Python 是 The Qt Company Ltd. 及其贡献者的作品，Qt 中的第三方代码有单独的版权和许可声明。
- Qt/PySide 的动态库保存在程序目录的 `_internal/PySide6/` 和 `_internal/shiboken6/`。退出程序后，接收者可以替换为 ABI 兼容的自行修改版本；为了调试对 LGPL 组件的修改而进行的逆向工程不受本项目许可证限制。源代码、构建脚本及可重新打包的程序源码均可获取。
- 本次使用的未经修改的上游源码文件及其 SHA-256 如下；这些文件也随本版本的 [Qt 源码归档](https://github.com/WQuan0717/VCGCA-Lite/releases/download/vision-v1.0.0/Qt-6.11.2-source-archives.zip)提供：

| 组件 | 上游源码 | SHA-256 |
| --- | --- | --- |
| PySide6 与 Shiboken | [pyside-setup 6.11.2](https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.11.2-src/pyside-setup-everywhere-src-6.11.2.tar.xz) | `cba47efbaad1bedd529725cbc14e21f156c7a19366f07b3edfbb076ffd7afdf8` |
| Qt Base | [qtbase 6.11.2](https://download.qt.io/official_releases/qt/6.11/6.11.2/submodules/qtbase-everywhere-src-6.11.2.tar.xz) | `5b2e00eccaf5a4d8c14134ffa0ea8dfd0a35ae1ffc7f8d87fa4305a1ed23cf22` |
| Qt SVG | [qtsvg 6.11.2](https://download.qt.io/official_releases/qt/6.11/6.11.2/submodules/qtsvg-everywhere-src-6.11.2.tar.xz) | `d594337feca84c26fb67fe87b85e6a5c12fda404b611d905f9d138210c311876` |
| Qt Image Formats | [qtimageformats 6.11.2](https://download.qt.io/official_releases/qt/6.11/6.11.2/submodules/qtimageformats-everywhere-src-6.11.2.tar.xz) | `cecd8900f34b6550076309bc94f62f828008b633a4239e0a08c86788f41001f8` |

源码构建步骤见 [Qt 构建说明](https://doc.qt.io/qt-6.11/build-sources.html) 和 [Qt for Python 构建说明](https://doc.qt.io/qtforpython-6.11/building_from_source/index.html)。Qt 官方按平台和构建配置提供的软件物料清单见 [Qt 许可与 SBOM 说明](https://doc.qt.io/qt-6.11/licensing.html)。

## MediaPipe、模型及隐私

- [MediaPipe 1.0.1](https://github.com/google-ai-edge/mediapipe) 及其上游通知采用 Apache License 2.0；随包保留了原版 `LICENSE` 和 `NOTICE`。
- `assets/models/gesture_recognizer.task` 是 Google MediaPipe 的原始 Gesture Recognizer 模型，未修改，SHA-256 为 `97952348cf6a6a4915c2ea1496b4b37ebabc50cbbf80571435643c455f2b0482`。它与 [LiteRT Community 官方模型记录](https://huggingface.co/litert-community/MediaPipe-GestureRecognizer/tree/cdc67a52ca3c423d75bb32c5e636a94a2163cf73)中的文件一致，该记录标注 Apache-2.0。Google 的原始下载地址为 <https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task>。
- 根据 [Google MediaPipe Tasks 隐私说明](https://developers.google.com/edge/mediapipe/solutions/privacy)，输入画面在设备上处理，MediaPipe Tasks 可能向 Google 发送 API 使用和性能指标。程序首次启动时在初始化识别服务前说明并征求同意；可从托盘菜单的“隐私说明”撤回并退出。

## 其他组件

- [OpenCV / opencv-contrib-python 5.0.0.93](https://github.com/opencv/opencv-python) 主要适用 Apache 2.0，其原始第三方许可证清单一并保留。本 Windows 包只使用摄像头功能，未分发 OpenCV 的可选 FFmpeg 插件。
- Python 3.11.17、NumPy 2.4.6、Pillow 12.3.0、Matplotlib 3.11.2 及其他实际构建依赖的版权和许可证见 `third_party/licenses/python/`；Pillow、NumPy 和 MediaPipe 的许可证文件也包含它们各自嵌入的第三方组件通知。Python、OpenSSL、Tcl/Tk、libffi、zlib、bzip2、libexpat、xz 和 Microsoft 运行库的相关许可证见 `third_party/licenses/native/`。
- [PyInstaller 6.22.3](https://pyinstaller.org/) 的 GPL 许可证包含允许分发打包程序的特殊例外；原文见 `third_party/licenses/python/pyinstaller/`。
- 安装器使用 [Inno Setup 6.7.3](https://jrsoftware.org/isinfo.php)，简体中文翻译来自 [Zhenghan Yang / kirakira 的翻译项目](https://github.com/kira-96/Inno-Setup-Chinese-Simplified-Translation)，采用 MIT 许可证。两者的原始许可及翻译的版权声明见 `third_party/licenses/installer/`。
- 本版本不使用 PyQt6、PyAutoGUI 或 MouseInfo；构建时也排除了 MediaPipe 未使用的音频输入组件及其 ASIO 库。

本文件仅说明本版本实际采用的上游许可和分发材料；各组件的完整许可条件以上游原文为准。
