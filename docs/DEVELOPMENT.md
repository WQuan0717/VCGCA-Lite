# 开发环境与本次修复

## 开发环境

使用项目专用 Conda 环境 `vcgca-lite`，本次验证的版本组合为：

- 默认路径：`%USERPROFILE%\.conda\envs\vcgca-lite`
- Python：3.11.17，64 位
- PyQt6：6.11.0
- MediaPipe：1.0.1
- OpenCV contrib：5.0.0.93
- NumPy：2.4.6
- 已安装 PyInstaller、pywin32、Pillow、PyAutoGUI 及测试工具。

如果当前 PowerShell 的 `python` 指向 Windows 应用别名，或 `conda` 不在 PATH 中，
可以从项目根目录直接调用环境中的解释器：

```powershell
./run.ps1
```

或者直接使用环境中的解释器：

```powershell
& "$env:USERPROFILE\.conda\envs\vcgca-lite\python.exe" main.py
& "$env:USERPROFILE\.conda\envs\vcgca-lite\python.exe" -m pytest -q
& "$env:USERPROFILE\.conda\envs\vcgca-lite\python.exe" scripts/check_environment.py
```

已加载 Conda 的终端也可以使用 `conda activate vcgca-lite`。
从另一台 Windows 电脑重建环境时，执行 README 中的 `conda env create -f environment.yml`。
`requirements-lock.txt` 保存本次通过依赖检查的完整版本组合。
请只安装一个提供 `cv2` 的发行包，本项目使用 `opencv-contrib-python`，
不要同时安装 `opencv-python` 或 headless 变体。

## 修复内容

| 场景 | 原问题 | 修复后的行为 |
| --- | --- | --- |
| 保存、读取、恢复设置 | 嵌套字典与默认值共享引用；非对象 JSON 导致启动异常 | 配置使用独立副本，异常格式回退到默认值，写入失败保留原文件 |
| 删除全部映射、恢复默认 | 空映射被自动恢复；部分常规控件未重置 | 空映射保持禁用；截图路径、剪贴板选项和托盘菜单选项一同恢复 |
| 双手同时出现 | 两只手可能拼成一个组合；识别结果排序变化导致误判 | 组合绑定开始准备的手，识别缓存按左右手记录，单只手消失也会发出丢失信号 |
| 丢失目标后恢复、时钟变化 | 超时后的第一帧仍可能执行旧动作；视频时间戳可能重复 | 处理响应前检查超时，状态计时使用单调时钟，模型输入时间戳严格递增 |
| 摄像头失败、服务停止和重启 | 失败路径泄漏资源；旧模型、识别缓存和错误状态残留；停止请求可能被初始化覆盖；默认采集后端首次取帧慢 | 所有退出路径释放并清空资源，重启重置会话，使用线程中断请求处理停止；Windows 优先 DirectShow，打开失败后回退到默认后端 |
| 窗口与映射编辑 | 提前打开调试窗口不能收到画面；允许不可执行的手势组合；静音 HUD 名称错误 | 预览提前订阅，拒绝无效组合并提示原因，关闭窗口释放对象，修正静音名称 |
| Windows 集成与打包 | 源码启动项缺少解释器，含空格路径未引用；互斥体未声明指针类型；安装器路径写死 | 启动项使用当前环境解释器并引用路径，声明 Windows API 类型，自动定位 Inno Setup 编译器 |

## 验证范围

- 30 项回归测试全部通过，包括真实 Windows 互斥体、完整手势组合重复触发、模拟摄像头异常、停止竞态、DirectShow 选择与失败回退，以及发布检查和设置快捷方式入口。
- 最初 15 项测试在原代码上有 14 项失败；修复后均通过。
- `python -m pip check` 通过，环境仅包含一个 OpenCV 发行包。
- 实际加载内置模型，对测试图像完成视频模式推理。
- 打包后的 windowed EXE 在移除 Conda 路径的环境中通过依赖、窗口、模型与摄像头两轮启停检查；应用与 EXE 文件版本均为 1.0.5。
- 实际读取小米 USB 摄像头的 640×480 画面并进行模型处理，连续两轮启动、停止服务均通过，检查分别记录 18 帧，停止后摄像头与模型资源均释放。
- 实际初始化设置、HUD、调试和日志窗口。该检查使用 Qt 离屏模式，未验证屏幕上的视觉布局。
- 测试使用临时用户目录，不覆盖已有配置，也不执行截图、音量或桌面控制。

运行摄像头检查前，需要在 Windows 摄像头隐私设置中允许桌面应用访问摄像头。
本次测试发现某 USB 摄像头使用默认采集后端时首帧延迟超过 8 秒，DirectShow 可以正常读取。
应用已改为 Windows 下优先使用 DirectShow。可运行：

```powershell
& "$env:USERPROFILE\.conda\envs\vcgca-lite\python.exe" scripts/check_environment.py --camera
```

带 `--camera` 的检查会读取摄像头并连续启动、停止服务两次，每轮收到第一帧后继续处理
约 1 秒；推理异常会使检查失败。系统控制动作保持禁用，不保存摄像头画面。
手势识别准确率和动作触发效果也需要在实际使用中观察，尤其是不同光线、摄像头及手部遮挡情况。

## 构建与发布检查

安装 Inno Setup 6 后，在专用环境中运行：

```powershell
python build_installer_onedir.py
```

编译器不在常见位置时，用 `INNO_SETUP_PATH` 指定 `ISCC.exe`。
版本来源为 `src/utils/version.py`；EXE 文件版本资源和安装器编译参数均从这里读取，
安装脚本还保留相同的默认版本以支持单独编译。
构建时的 DLL 扫描目录限制为当前环境、Qt 与 Windows 系统目录，既收集 Conda 的原生依赖，
也避免从宿主工具 PATH 中混入同名、不兼容的库。

打包后的应用支持隔离检查，无需另装 Python：

```powershell
./output/onedir/VCGCA-Lite/VCGCA-Lite.exe --check-environment --camera --report ./output/packaged-check.json
```

正常启动时使用 `VCGCA-Lite.exe`；`--settings` 用于直接打开设置窗口。
安装包输出到 `installer_output/`，发布的校验值由最终安装包和便携 ZIP 计算。
