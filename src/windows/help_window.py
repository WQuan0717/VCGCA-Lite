from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QFrame, QTabWidget,
                             QTextBrowser, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QColor

from src.utils.version import get_version_string, APP_NAME, BUILD_DATE, COPYRIGHT


class HelpWindow(QMainWindow):
    """帮助文档窗口"""
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("帮助文档")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1000, 800)

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            QTextBrowser {
                border: none;
                background-color: white;
                padding: 20px;
                font-size: 14px;
                line-height: 1.6;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel("📖 VCGCA-Lite 帮助文档")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 版本信息
        version = get_version_string()
        version_label = QLabel(f"版本: {version} | 手势控制截图助手")
        version_label.setStyleSheet("color: #666; font-size: 12px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        layout.addSpacing(10)

        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_guide_tab(), "📚 使用指南")
        self.tab_widget.addTab(self.create_gesture_tab(), "👋 手势说明")
        self.tab_widget.addTab(self.create_shortcut_tab(), "⌨️ 快捷键")
        self.tab_widget.addTab(self.create_about_tab(), "ℹ️ 关于")
        layout.addWidget(self.tab_widget)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def create_guide_tab(self):
        """创建使用指南标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        content.setHtml("""
        <html>
        <head>
            <style>
                body { font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }
                h3 { color: #333; margin-top: 25px; }
                .step { background: #f0f7ff; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; border-radius: 4px; }
                .tip { background: #fff3e0; padding: 15px; margin: 10px 0; border-left: 4px solid #FF9800; border-radius: 4px; }
                .warning { background: #ffebee; padding: 15px; margin: 10px 0; border-left: 4px solid #f44336; border-radius: 4px; }
                code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
                ul { margin: 10px 0; }
                li { margin: 5px 0; }
            </style>
        </head>
        <body>
            <h2>🚀 快速入门</h2>
            
            <h3>1. 启动程序</h3>
            <div class="step">
                <p><strong>方法一：</strong>双击 VCGCA-Lite.exe 启动程序</p>
                <p><strong>方法二：</strong>设置开机自启动，系统启动时自动运行</p>
                <p>启动后，程序会在系统托盘显示图标，手势识别服务会自动开始</p>
            </div>

            <h3>2. 基本使用流程</h3>
            <div class="step">
                <p><strong>步骤 1：</strong>确保摄像头正常工作，程序会自动检测</p>
                <p><strong>步骤 2：</strong>在摄像头前做出特定手势（详见"手势说明"标签页）</p>
                <p><strong>步骤 3：</strong>保持手势稳定，等待识别完成</p>
                <p><strong>步骤 4：</strong>听到提示音或看到屏幕闪光，表示截图成功</p>
                <p><strong>步骤 5：</strong>截图已保存到指定目录，可直接使用</p>
            </div>

            <h3>3. 系统托盘菜单</h3>
            <p>右键点击托盘图标可以访问以下功能：</p>
            <ul>
                <li><strong>显示设置</strong> - 打开设置窗口，配置程序参数</li>
                <li><strong>启用/禁用HUD</strong> - 切换屏幕提示功能</li>
                <li><strong>显示调试窗口</strong> - 查看实时识别状态和摄像头画面</li>
                <li><strong>查看日志</strong> - 打开日志查看器，排查问题</li>
                <li><strong>退出</strong> - 关闭程序</li>
            </ul>

            <h3>4. 设置说明</h3>
            <div class="tip">
                <p><strong>通用设置</strong></p>
                <ul>
                    <li><strong>开机自启动：</strong>Windows 启动时自动运行程序</li>
                    <li><strong>显示启动动画：</strong>启动时显示欢迎画面</li>
                </ul>
            </div>

            <div class="tip">
                <p><strong>截图设置</strong></p>
                <ul>
                    <li><strong>保存路径：</strong>设置截图文件的保存位置</li>
                    <li><strong>文件格式：</strong>支持 PNG、JPG、BMP 格式</li>
                    <li><strong>文件前缀：</strong>截图文件名的前缀标识</li>
                </ul>
            </div>

            <div class="tip">
                <p><strong>手势设置</strong></p>
                <ul>
                    <li><strong>摄像头：</strong>选择使用的摄像头设备</li>
                    <li><strong>识别阈值：</strong>调整手势识别的灵敏度</li>
                    <li><strong>准备时间：</strong>手势保持时间（防止误触发）</li>
                    <li><strong>冷静期：</strong>两次截图之间的最小间隔</li>
                </ul>
            </div>

            <div class="tip">
                <p><strong>显示设置</strong></p>
                <ul>
                    <li><strong>启用HUD：</strong>在屏幕上显示识别状态提示</li>
                    <li><strong>显示截图闪光：</strong>截图时显示全屏闪光效果</li>
                </ul>
            </div>

            <h3>5. 常见问题</h3>
            <div class="warning">
                <p><strong>Q: 程序无法启动？</strong></p>
                <p>A: 请检查是否安装了摄像头驱动，或尝试以管理员身份运行程序。</p>
            </div>

            <div class="warning">
                <p><strong>Q: 手势无法识别？</strong></p>
                <p>A: 确保光线充足，手势清晰可见。可以在调试窗口查看识别状态。</p>
            </div>

            <div class="warning">
                <p><strong>Q: 截图保存到哪里了？</strong></p>
                <p>A: 默认保存在程序目录的 screenshots 文件夹中，可在设置中更改。</p>
            </div>

            <div class="warning">
                <p><strong>Q: 如何关闭程序？</strong></p>
                <p>A: 右键点击系统托盘图标，选择"退出"。</p>
            </div>
        </body>
        </html>
        """)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        return widget

    def create_gesture_tab(self):
        """创建手势说明标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QTextBrowser()
        content.setHtml("""
        <html>
        <head>
            <style>
                body { font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }
                h3 { color: #333; margin-top: 25px; }
                .gesture-card { 
                    background: #f8f9fa; 
                    padding: 20px; 
                    margin: 15px 0; 
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }
                .gesture-name { 
                    font-size: 18px; 
                    font-weight: bold; 
                    color: #2196F3;
                    margin-bottom: 10px;
                }
                .gesture-desc { 
                    color: #666;
                    margin: 10px 0;
                }
                .gesture-action {
                    background: #e3f2fd;
                    padding: 10px;
                    border-radius: 4px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                .tip { background: #fff3e0; padding: 15px; margin: 10px 0; border-left: 4px solid #FF9800; border-radius: 4px; }
                .note { background: #e8f5e9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; border-radius: 4px; }
                table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                th { background: #2196F3; color: white; padding: 12px; text-align: left; }
                td { padding: 12px; border-bottom: 1px solid #ddd; }
                tr:hover { background: #f5f5f5; }
            </style>
        </head>
        <body>
            <h2>👋 支持的手势</h2>
            
            <div class="note">
                <p><strong>💡 使用提示</strong></p>
                <p>所有手势都需要保持 <strong>1-2 秒</strong> 才能触发，这是为了防止误操作。
                保持手势稳定，直到看到屏幕提示或听到提示音。</p>
            </div>

            <h3>📸 截图手势</h3>
            
            <div class="gesture-card">
                <div class="gesture-name">✌️ 剪刀手 (Victory)</div>
                <div class="gesture-desc">
                    <p><strong>手势描述：</strong>伸出食指和中指，形成"V"字形，其他手指握拳</p>
                    <p><strong>识别要点：</strong></p>
                    <ul>
                        <li>食指和中指伸直分开</li>
                        <li>无名指和小指弯曲握拳</li>
                        <li>拇指可以自然放置</li>
                    </ul>
                </div>
                <div class="gesture-action">
                    🎯 触发动作：全屏截图
                </div>
            </div>

            <div class="gesture-card">
                <div class="gesture-name">👍 点赞 (Thumb Up)</div>
                <div class="gesture-desc">
                    <p><strong>手势描述：</strong>竖起大拇指，其他四指握拳</p>
                    <p><strong>识别要点：</strong></p>
                    <ul>
                        <li>大拇指向上伸直</li>
                        <li>其他四指弯曲握拳</li>
                        <li>手掌朝向摄像头</li>
                    </ul>
                </div>
                <div class="gesture-action">
                    🎯 触发动作：全屏截图
                </div>
            </div>

            <div class="gesture-card">
                <div class="gesture-name">👎 点踩 (Thumb Down)</div>
                <div class="gesture-desc">
                    <p><strong>手势描述：</strong>大拇指向下，其他四指握拳</p>
                    <p><strong>识别要点：</strong></p>
                    <ul>
                        <li>大拇指向下伸直</li>
                        <li>其他四指弯曲握拳</li>
                        <li>手掌朝向摄像头</li>
                    </ul>
                </div>
                <div class="gesture-action">
                    🎯 触发动作：全屏截图
                </div>
            </div>

            <div class="gesture-card">
                <div class="gesture-name">☝️ 食指指天 (Pointing Up)</div>
                <div class="gesture-desc">
                    <p><strong>手势描述：</strong>食指向上伸直，其他手指握拳</p>
                    <p><strong>识别要点：</strong></p>
                    <ul>
                        <li>食指向上伸直</li>
                        <li>中指、无名指、小指弯曲握拳</li>
                        <li>拇指可以自然放置</li>
                    </ul>
                </div>
                <div class="gesture-action">
                    🎯 触发动作：全屏截图
                </div>
            </div>

            <div class="gesture-card">
                <div class="gesture-name">✊ 握拳 (Closed Fist)</div>
                <div class="gesture-desc">
                    <p><strong>手势描述：</strong>五指全部弯曲握拳</p>
                    <p><strong>识别要点：</strong></p>
                    <ul>
                        <li>所有手指弯曲握拳</li>
                        <li>拇指可以压在手指上或自然放置</li>
                        <li>手掌朝向摄像头</li>
                    </ul>
                </div>
                <div class="gesture-action">
                    🎯 触发动作：全屏截图
                </div>
            </div>

            <div class="gesture-card">
                <div class="gesture-name">🖐️ 张开手掌 (Open Palm)</div>
                <div class="gesture-desc">
                    <p><strong>手势描述：</strong>五指伸直张开</p>
                    <p><strong>识别要点：</strong></p>
                    <ul>
                        <li>五指全部伸直</li>
                        <li>手指自然分开</li>
                        <li>手掌朝向摄像头</li>
                    </ul>
                </div>
                <div class="gesture-action">
                    🎯 触发动作：全屏截图
                </div>
            </div>

            <h3>📋 手势识别状态说明</h3>
            <table>
                <tr>
                    <th>状态</th>
                    <th>说明</th>
                    <th>HUD显示</th>
                </tr>
                <tr>
                    <td>空闲</td>
                    <td>等待手势输入</td>
                    <td>无显示</td>
                </tr>
                <tr>
                    <td>准备等待</td>
                    <td>检测到手势，等待确认</td>
                    <td>显示"就绪"</td>
                </tr>
                <tr>
                    <td>变化等待</td>
                    <td>手势变化检测中</td>
                    <td>显示"就绪"</td>
                </tr>
                <tr>
                    <td>冷静期</td>
                    <td>截图后冷却时间</td>
                    <td>显示动作名</td>
                </tr>
            </table>

            <div class="tip">
                <p><strong>🎥 摄像头使用建议</strong></p>
                <ul>
                    <li>确保光线充足，避免背光</li>
                    <li>手势距离摄像头 30-100 厘米最佳</li>
                    <li>保持手部在画面中央</li>
                    <li>避免快速移动，保持稳定</li>
                </ul>
            </div>
        </body>
        </html>
        """)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        return widget

    def create_shortcut_tab(self):
        """创建快捷键标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QTextBrowser()
        content.setHtml("""
        <html>
        <head>
            <style>
                body { font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }
                h3 { color: #333; margin-top: 25px; }
                .shortcut-section { margin: 20px 0; }
                table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                th { background: #2196F3; color: white; padding: 12px; text-align: left; }
                td { padding: 12px; border-bottom: 1px solid #ddd; }
                tr:hover { background: #f5f5f5; }
                .key { 
                    background: #f5f5f5; 
                    padding: 4px 10px; 
                    border-radius: 4px; 
                    border: 1px solid #ddd;
                    font-family: monospace;
                    font-size: 13px;
                }
                .tip { background: #fff3e0; padding: 15px; margin: 10px 0; border-left: 4px solid #FF9800; border-radius: 4px; }
                .note { background: #e8f5e9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h2>⌨️ 快捷键列表</h2>
            
            <div class="note">
                <p><strong>💡 提示</strong></p>
                <p>以下快捷键在程序运行时全局可用。如果快捷键与其他软件冲突，
                可以在设置中修改或禁用。</p>
            </div>

            <div class="shortcut-section">
                <h3>🎯 截图快捷键</h3>
                <table>
                    <tr>
                        <th>快捷键</th>
                        <th>功能</th>
                        <th>说明</th>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">Shift</span> + <span class="key">S</span></td>
                        <td>全屏截图</td>
                        <td>立即截取整个屏幕</td>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">Shift</span> + <span class="key">A</span></td>
                        <td>区域截图</td>
                        <td>选择屏幕区域进行截图</td>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">Shift</span> + <span class="key">W</span></td>
                        <td>窗口截图</td>
                        <td>截取当前活动窗口</td>
                    </tr>
                </table>
            </div>

            <div class="shortcut-section">
                <h3>⚙️ 程序控制快捷键</h3>
                <table>
                    <tr>
                        <th>快捷键</th>
                        <th>功能</th>
                        <th>说明</th>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">Shift</span> + <span class="key">G</span></td>
                        <td>切换手势识别</td>
                        <td>启用/禁用手势识别功能</td>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">Shift</span> + <span class="key">H</span></td>
                        <td>切换 HUD 显示</td>
                        <td>显示/隐藏屏幕提示</td>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">Shift</span> + <span class="key">D</span></td>
                        <td>打开调试窗口</td>
                        <td>显示实时识别状态</td>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">Shift</span> + <span class="key">O</span></td>
                        <td>打开截图文件夹</td>
                        <td>快速打开截图保存目录</td>
                    </tr>
                </table>
            </div>

            <div class="shortcut-section">
                <h3>🪟 窗口快捷键</h3>
                <table>
                    <tr>
                        <th>快捷键</th>
                        <th>功能</th>
                        <th>说明</th>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">,</span></td>
                        <td>打开设置</td>
                        <td>显示设置窗口</td>
                    </tr>
                    <tr>
                        <td><span class="key">F1</span></td>
                        <td>打开帮助</td>
                        <td>显示帮助文档</td>
                    </tr>
                    <tr>
                        <td><span class="key">Esc</span></td>
                        <td>关闭窗口</td>
                        <td>关闭当前打开的窗口</td>
                    </tr>
                    <tr>
                        <td><span class="key">Ctrl</span> + <span class="key">Q</span></td>
                        <td>退出程序</td>
                        <td>完全退出应用程序</td>
                    </tr>
                </table>
            </div>

            <div class="tip">
                <p><strong>📝 自定义快捷键</strong></p>
                <p>目前版本暂不支持自定义快捷键，将在后续版本中添加此功能。
                如需修改快捷键，请编辑配置文件或联系开发者。</p>
            </div>

            <div class="shortcut-section">
                <h3>🖱️ 托盘图标操作</h3>
                <table>
                    <tr>
                        <th>操作</th>
                        <th>功能</th>
                    </tr>
                    <tr>
                        <td>左键单击</td>
                        <td>显示/隐藏设置窗口</td>
                    </tr>
                    <tr>
                        <td>左键双击</td>
                        <td>打开设置窗口</td>
                    </tr>
                    <tr>
                        <td>右键单击</td>
                        <td>显示上下文菜单</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        return widget

    def create_about_tab(self):
        """创建关于标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 获取版本信息
        version = get_version_string()
        build_date = BUILD_DATE
        copyright_text = COPYRIGHT

        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        content.setHtml(f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; }}
                .about-container {{ text-align: center; padding: 40px 20px; }}
                .app-name {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #2196F3;
                    margin: 20px 0;
                }}
                .version {{
                    font-size: 16px;
                    color: #666;
                    margin: 10px 0;
                }}
                .description {{
                    font-size: 14px;
                    color: #666;
                    margin: 20px 0;
                    max-width: 500px;
                    margin-left: auto;
                    margin-right: auto;
                }}
                .section {{
                    background: #f8f9fa;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                    text-align: left;
                }}
                .section-title {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 10px;
                }}
                .info-row {{
                    margin: 8px 0;
                    color: #666;
                }}
                .label {{
                    font-weight: bold;
                    color: #333;
                }}
                .link {{
                    color: #2196F3;
                    text-decoration: none;
                }}
                .link:hover {{
                    text-decoration: underline;
                }}
                .copyright {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #999;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="about-container">
                <div class="app-name">VCGCA-Lite</div>
                <div class="version">版本 {version}</div>
                <div class="description">
                    基于计算机视觉的手势控制截图助手<br>
                    通过摄像头识别手势，实现免接触式截图操作
                </div>

                <div class="section">
                    <div class="section-title">📋 软件信息</div>
                    <div class="info-row"><span class="label">软件名称：</span>VCGCA-Lite (Vision-based Gesture Control Assistant)</div>
                    <div class="info-row"><span class="label">当前版本：</span>{version}</div>
                    <div class="info-row"><span class="label">发布日期：</span>{build_date}</div>
                    <div class="info-row"><span class="label">运行平台：</span>Windows 10/11</div>
                    <div class="info-row"><span class="label">开发语言：</span>Python 3.11</div>
                    <div class="info-row"><span class="label">界面框架：</span>PyQt6</div>
                </div>

                <div class="section">
                    <div class="section-title">🙏 致谢</div>
                    <div class="info-row">本软件使用了以下开源项目：</div>
                    <div class="info-row">• <a href="https://mediapipe.dev/" class="link">MediaPipe</a> - 手势识别引擎</div>
                    <div class="info-row">• <a href="https://www.qt.io/" class="link">Qt</a> - 图形界面框架</div>
                    <div class="info-row">• <a href="https://opencv.org/" class="link">OpenCV</a> - 计算机视觉库</div>
                    <div class="info-row">• <a href="https://www.python.org/" class="link">Python</a> - 编程语言</div>
                </div>

                <div class="section">
                    <div class="section-title">📄 开源协议</div>
                    <div class="info-row">本软件基于 MIT 协议开源</div>
                    <div class="info-row">您可以自由使用、修改和分发本软件</div>
                </div>

                <div class="copyright">
                    <p>{copyright_text} VCGCA-Lite. All rights reserved.</p>
                    <p>本软件按"原样"提供，不提供任何明示或暗示的担保。</p>
                </div>
            </div>
        </body>
        </html>
        """)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        return widget

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
