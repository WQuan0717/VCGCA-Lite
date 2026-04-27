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

| 手势 | 描述 |
|------|------|
| ✋ 张开手掌 (Open_Palm) | 五指伸直张开 |
| ✊ 握拳 (Closed_Fist) | 五指全部弯曲握拳 |
| 👍 点赞 (Thumb_Up) | 竖起大拇指 |
| 👎 点踩 (Thumb_Down) | 大拇指向下 |
| ☝️ 食指指天 (Pointing_Up) | 食指向上伸直 |
| ✌️ 剪刀手 (Victory) | 伸出食指和中指形成"V"字 |

## 默认手势控制

| 准备手势 | 响应手势 | 功能 |
|---------|---------|------|
| 张开手掌 | 握拳 | 截图并保存 |
| 张开手掌 | 点赞 | 增大音量 |
| 张开手掌 | 点踩 | 减小音量 |
| 剪刀手 | 食指指天 | 显示桌面 |

## 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.10+ (运行源码)
- **硬件**: 摄像头，4GB+ 内存
- **权限**: 屏幕截图和系统控制权限

## 下载安装

### 正式版安装包

从 [Releases](https://github.com/WQuan0717/VCGCA/releases) 页面下载最新版本：

- `VCGCA-Lite-Setup-v1.0.0.exe` - Windows 安装程序

### 源码运行

```bash
# 克隆仓库
git clone https://github.com/WQuan0717/VCGCA.git
cd VCGCA

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 使用方法

1. **启动程序**：运行 VCGCA-Lite.exe 或 `python main.py`
2. **系统托盘**：右键点击托盘图标访问功能菜单
3. **手势控制**：
   - 将手放在摄像头前
   - 做出准备手势并保持 0.5 秒
   - 快速切换到响应手势
   - 看到屏幕闪光表示触发成功

### 手势控制流程

```
空闲状态 → 准备手势 → 保持0.5秒 → 变化等待 → 响应手势 → 执行功能 → 冷静期
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
├── docs/                      # 文档
│   ├── README.md
│   └── CHANGELOG.md
├── build_exe_onedir.py        # 构建脚本
├── build_installer_onedir.py  # 安装包构建脚本
├── installer_onedir.iss       # Inno Setup 脚本
├── ChineseSimplified.isl      # 简体中文语言文件
├── requirements.txt           # Python 依赖
├── main.py                    # 程序入口
└── README.md                  # 本文件
```

## 配置说明

程序设置保存在 `%APPDATA%\VCGCA-Lite\settings.json`

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

### 构建可执行文件

```bash
python build_exe_onedir.py
```

输出目录：`output/onedir/VCGCA-Lite/`

### 构建安装包

```bash
python build_installer_onedir.py
```

输出文件：`installer_output/VCGCA-Lite-Setup-v{version}.exe`

## 技术栈

- **计算机视觉**: OpenCV, MediaPipe
- **GUI 框架**: PyQt6
- **系统控制**: pyautogui, Windows API
- **打包工具**: PyInstaller, Inno Setup

## 许可证

MIT License

## 更新日志

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
