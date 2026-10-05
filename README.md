# VCGCA-Lite

视觉手势控制系统 (Vision-based Gesture Control Application Lite)

基于 MediaPipe 的轻量级手势识别系统，通过摄像头捕捉手势动作，实现无接触式电脑控制。

## 功能特性

- **手势识别**：基于 MediaPipe 的手势检测和识别
- **系统控制**：支持截图、音量控制、显示桌面等功能
- **自定义手势映射**：可配置不同手势组合触发的功能
- **实时 HUD 提示**：屏幕悬浮窗显示当前识别状态
- **截图管理**：支持自定义截图保存路径，一键打开截图文件夹
- **剪贴板集成**：截图后自动复制到剪贴板（可选）
- **系统托盘**：最小化到系统托盘，后台运行
- **日志系统**：完整的日志记录和查看功能
- **单实例保护**：防止程序重复启动

## 支持的手势

| 手势                     | 描述            |
| ---------------------- | ------------- |
| ✋ 张开手掌 (Open\_Palm)    | 五指伸直张开        |
| ✊ 握拳 (Closed\_Fist)    | 五指全部弯曲握拳      |
| 👍 点赞 (Thumb\_Up)      | 竖起大拇指         |
| 👎 点踩 (Thumb\_Down)    | 大拇指向下         |
| ☝️ 食指指天 (Pointing\_Up) | 食指向上伸直        |
| ✌️ 剪刀手 (Victory)       | 伸出食指和中指形成"V"字 |

## 默认手势控制

| 准备手势 | 响应手势 | 功能    |
| ---- | ---- | ----- |
| 张开手掌 | 握拳   | 截图并保存 |
| 张开手掌 | 点赞   | 音量增大  |
| 张开手掌 | 点踩   | 音量减小  |
| 剪刀手  | 食指指天 | 显示桌面  |

## 系统要求

- **操作系统**: Windows 10/11
- **Python**: 推荐使用独立的 Python 3.11 64 位环境（见下方开发环境配置）
- **硬件**: 摄像头，4GB+ 内存
- **权限**: 屏幕截图和系统控制权限

## 下载安装

### 正式版安装包

从 [Releases](https://github.com/WQuan0717/VCGCA-Lite/releases) 页面下载最新版本：

- `VCGCA-Lite-Setup-v1.0.5.exe` - Windows x64 安装程序
- `VCGCA-Lite-v1.0.5-windows-x64.zip` - 解压即可运行的便携版

### 源码运行

```bash
# 克隆仓库
git clone https://github.com/WQuan0717/VCGCA-Lite.git
cd VCGCA-Lite

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### Conda 开发环境

在已配置 Conda 的终端中执行：

```powershell
conda env create -f environment.yml
conda activate vcgca-lite
python -m pip check
python -m pytest -q
python main.py
```

依赖使用 `requirements.txt`；`requirements-dev.txt` 额外安装回归测试工具。
`requirements-lock.txt` 记录 Windows / Python 3.11 环境中实际验证过的完整依赖版本，
需要复现该环境时可执行 `python -m pip install -r requirements-lock.txt`。

如果当前 PowerShell 尚未加载 Conda，可使用 `./run.ps1` 直接调用用户目录下
`.conda/envs/vcgca-lite/python.exe`。环境安装在其他位置时，使用
`./run.ps1 -PythonPath '实际环境路径/python.exe'`。

完整的本机配置与修复记录见 [开发说明](docs/DEVELOPMENT.md)。

`python scripts/check_environment.py` 检查依赖、内置模型和窗口初始化。
加上 `--camera` 可验证摄像头读取与服务重启；检查过程中禁用系统控制动作，
使用临时配置目录，不会覆盖已有设置或保存摄像头画面。

## 使用方法

1. **启动程序**：运行  `python main.py`
2. **系统托盘**：右键点击托盘图标访问功能菜单
3. **手势控制**：
   - 将手放在摄像头前
   - 做出准备手势并保持 1.0 秒，HUD显示"就绪"
   - 快速切换到响应手势
   - HUD显示触发的"动作名"

### 手势控制流程

```
空闲状态 → 准备手势 → 保持1.0秒 → 变化等待 → 响应手势 → 执行功能 → 冷静期
```

## 项目结构

```
VCGCA-Lite/
├── src/                       # 源代码
│   ├── core/                  # 核心功能
│   │   ├── gesture_controller.py    # 手势控制器
│   │   ├── gesture_service.py       # 手势识别服务
│   │   └── system_control.py        # 系统控制功能
│   ├── utils/                 # 工具模块
│   │   ├── settings_manager.py      # 设置管理
│   │   ├── logger.py                # 日志系统
│   │   ├── error_handler.py         # 错误处理
│   │   ├── startup_manager.py       # 开机启动管理
│   │   ├── single_instance.py       # 单实例检测
│   │   ├── icon_helper.py           # 图标工具
│   │   ├── gesture_names.py         # 手势名称映射
│   │   └── version.py               # 版本信息
│   ├── windows/               # UI 窗口
│   │   ├── settings_window.py       # 设置窗口
│   │   ├── hud_window.py            # HUD 悬浮窗
│   │   ├── debug_window.py          # 调试窗口
│   │   ├── log_window.py            # 日志查看器
│   │   ├── splash_window.py         # 启动动画
│   │   └── gesture_mapping_dialog.py # 手势映射对话框
│   └── tray_app.py            # 托盘应用程序
├── tests/                     # 回归测试
├── scripts/check_environment.py # 环境与运行检查
├── environment.yml            # Conda 开发环境
├── requirements-dev.txt       # 开发依赖
├── requirements-lock.txt      # 已验证的完整依赖版本
├── run.ps1                    # PowerShell 启动脚本
├── build_exe_onedir.py        # 构建脚本
├── build_installer_onedir.py  # 安装包构建脚本
├── installer_onedir.iss       # Inno Setup 脚本
├── ChineseSimplified.isl      # 简体中文语言文件
├── requirements.txt           # Python 依赖
├── main.py                    # 程序入口
└── README.md                  # 本文件
```

## 配置说明

程序设置保存在 `%USERPROFILE%\.vcgca-lite\settings.json`，日志为同目录下的 `app.log`。
内置识别模型首次使用时复制到 `%USERPROFILE%\.vcgca-lite\models\`。

### 可配置项

- **常规设置**
  - 开机自动启动
  - 显示启动动画
  - 截图后复制到剪贴板
  - 截图保存路径
  - 托盘菜单显示选项
- **显示设置**
  - HUD 透明度
  - HUD 窗口大小
  - HUD 位置（水平/垂直）
- **手势控制设置**
  - 准备时间（毫秒）
  - 变化时间（毫秒）
  - 冷静时间（毫秒）
  - 手势功能映射

## 构建发布

### 构建可执行文件（构建程序目录，不需要手动执行）

```bash
# python build_exe_onedir.py
```

输出目录：`output/onedir/VCGCA-Lite/`

### 构建安装包（会自动调用 build\_exe\_onedir.py 用于构建程序目录）

安装包构建额外需要 Inno Setup 6。脚本会检查 PATH 和常见安装目录；
自定义安装位置可用环境变量 `INNO_SETUP_PATH` 指定 `ISCC.exe` 的完整路径。

```bash
python build_installer_onedir.py
```

输出文件：`installer_output/VCGCA-Lite-Setup-v{version}.exe`

### 构建输出目录说明

运行构建脚本后会生成以下三个目录，各自用途如下：

| 目录                          | 用途                 | 说明                                                      |
| --------------------------- | ------------------ | ------------------------------------------------------- |
| `build_onedir/`             | PyInstaller 临时工作目录 | 存放构建过程中的临时文件和缓存，**可以删除**                                |
| `output/onedir/VCGCA-Lite/` | 应用程序目录             | 包含完整的可执行程序和所有依赖，**可直接运行**或用于重新打包                        |
| `installer_output/`         | 安装包输出目录            | 包含最终生成的 `VCGCA-Lite-Setup-v{version}.exe` 安装程序，**用于分发** |

**清理建议**：

- 如果只需要最终安装包，可以删除 `build_onedir/` 和 `output/` 目录
- 如需重新打包安装程序但不需要重新构建 EXE，保留 `output/onedir/VCGCA-Lite/` 即可
- `installer_output/` 中的 `.exe` 文件是最终交付物，建议备份

## 技术栈

- **计算机视觉**: OpenCV, MediaPipe
- **GUI 框架**: PyQt6
- **系统控制**: pyautogui, Windows API
- **打包工具**: PyInstaller, Inno Setup

## 许可证

MIT License

## 更新日志

### v1.0.5 (2026-10-05)

- 修复双手手势串用、目标丢失和超时后误触发。
- 修复空手势映射被恢复、默认设置共享引用及恢复默认不完整。
- 修复摄像头异常、服务停止和重启时的资源释放与状态残留。
- Windows 摄像头优先使用 DirectShow，失败时回退默认采集后端。
- 修复调试预览、无效映射、静音提示、源码开机启动与设置快捷方式。
- 增加专用 Conda 环境、依赖锁定、回归测试和打包后运行检查。
- 统一应用、EXE 版本信息与安装包版本号，修正安装器互斥体和仓库链接。
- 修复 Conda 打包中的原生 DLL 收集与宿主 PATH 同名库冲突。

### v1.0.0 (2026-04-27)

- 正式发布
- 基于 MediaPipe 的手势识别
- 支持自定义手势功能映射
- 截图保存路径自定义
- 系统托盘集成
- 完整的日志系统
- 单实例保护
- 中文安装界面

## 致谢

- [MediaPipe](https://mediapipe.dev/) - 手势检测框架
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [Inno Setup](https://jrsoftware.org/isinfo.php) - 安装包制作工具

