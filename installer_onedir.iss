; VCGCA-Lite onedir 模式安装脚本
; 使用 Inno Setup 6 编译

#define MyAppName "VCGCA-Lite"
#define MyAppVersion "0.3.1"
#define MyAppPublisher "VCGCA"
#define MyAppURL "https://github.com/vcgca/vcgca-lite"
#define MyAppExeName "VCGCA-Lite.exe"

[Setup]
; 应用信息
AppId={{B8F5D3A1-4E2C-4B9A-9F6D-3E8C2A1B5D4F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 默认安装路径
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes

; 输出设置
OutputDir=installer_output
OutputBaseFilename=VCGCA-Lite-Setup-v{#MyAppVersion}
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

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; onedir 模式：复制整个文件夹
Source: "output\onedir\VCGCA-Lite\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 文档
Source: "docs\README.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "docs\CHANGELOG.md"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
; 开始菜单快捷方式
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} 设置"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--settings"

; 桌面快捷方式（可选）
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 安装完成后启动程序
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除的文件和目录
Type: filesandordirs; Name: "{app}"

[Code]
// 初始化安装程序
function InitializeSetup(): Boolean;
begin
  Result := true;
  
  // 检查是否已运行
  if CheckForMutexes('VCGCA-Lite-Running') then
  begin
    MsgBox('VCGCA-Lite 正在运行，请先关闭程序后再安装。', mbError, MB_OK);
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
      DelTree(ExpandConstant('{userappdata}\VCGCA-Lite'), True, True, True);
    end;
  end;
end;
