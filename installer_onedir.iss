; 视觉手势控制系统 onedir 模式安装脚本
; 使用 Inno Setup 6 编译

#ifndef MyAppName
  #define MyAppName "视觉手势控制系统"
#endif
#ifndef MyAppBinaryName
  #define MyAppBinaryName "VisionGestureControl"
#endif
#ifndef MyAppMutex
  #define MyAppMutex "VisionGestureControl-SingleInstance"
#endif
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppPublisher "个人开发者"
#define MyAppURL "https://github.com/WQuan0717/VCGCA-Lite"
#define MyAppExeName MyAppBinaryName + ".exe"

[Setup]
; 应用信息
AppId={{BCBF102B-3EA8-4D3F-8407-EA939F3C6A1A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppMutex={#MyAppMutex}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 默认安装路径
DefaultDirName={autopf}\{#MyAppBinaryName}
DisableProgramGroupPage=yes

; 输出设置
OutputDir=installer_output
OutputBaseFilename={#MyAppBinaryName}-Setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; 权限要求
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; 版本信息
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} 安装程序
VersionInfoCopyright=Copyright (C) 2026 {#MyAppPublisher}

; 图标设置
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
; 旧的改名测试版曾包含这些不再使用的可选运行库。只清理应用自身的
; 已知组件目录和文件，不触碰用户设置、截图或其他安装目录内容。
Type: filesandordirs; Name: "{app}\_internal\PyQt6"
Type: filesandordirs; Name: "{app}\_internal\_sounddevice_data"
Type: files; Name: "{app}\_internal\cv2\opencv_videoio_ffmpeg*.dll"

[Files]
; onedir 模式：复制整个应用程序文件夹
Source: "output\onedir\{#MyAppBinaryName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 开始菜单快捷方式
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} 设置"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--settings"

; 桌面快捷方式（可选）
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 安装完成后启动程序
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// 初始化安装程序
function InitializeSetup(): Boolean;
begin
  Result := true;
  
  // 检查是否已运行
  if CheckForMutexes('{#MyAppMutex}') then
  begin
    MsgBox('{#MyAppName}正在运行，请先关闭程序后再安装。', mbError, MB_OK);
    Result := false;
    Exit;
  end;
end;

// 卸载步骤变化时
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // 询问是否删除用户配置
    if MsgBox('是否删除用户配置文件和设置？', mbConfirmation, MB_YESNO) = IDYES then
    begin
      // 只删除新版本自己的设置；旧版数据不会自动迁移或删除。
      DelTree(ExpandConstant('{%USERPROFILE}\.vision-gesture-control'), True, True, True);
    end;
  end;
end;
