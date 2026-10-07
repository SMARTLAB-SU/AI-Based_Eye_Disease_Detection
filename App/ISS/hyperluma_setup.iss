; ============================================================
; HYPERLUMA - Eye Disease Detection & Spectral Analysis System
; SMART - Sanjivani Multidisciplinary AI Research & Technology
; hyperluma_setup.iss - Inno Setup Windows Installer Script (v2.0.0)
; ============================================================

#define MyAppName "HYPERLUMA"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "SMART - Sanjivani Multidisciplinary AI Research & Technology"
#define MyAppExeName "HYPERLUMA.exe"
#define MyAppDescription "Professional Eye Disease Detection & Spectral Analysis System"

[Setup]
AppId={{C3D4E5F6-A7B8-9012-CDEF-123456789012}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://sanjivani.edu.in
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=no
OutputDir=Output
OutputBaseFilename=HYPERLUMA_Setup_v2.0.0
SetupIconFile=..\Source Code\assets\smartlab_logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop shortcut for HYPERLUMA"; GroupDescription: "Desktop Shortcuts:"
Name: "startmenuicon"; Description: "Create Start Menu shortcuts"; GroupDescription: "Start Menu Shortcuts:"

[Dirs]
Name: "{app}"; Permissions: everyone-full
Name: "{app}\Models"; Permissions: everyone-full
Name: "{app}\assets"; Permissions: everyone-full
Name: "{app}\logs"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}"; Permissions: everyone-full

[Files]
; Main Executable
Source: "..\..\HYPERLUMA.exe"; DestDir: "{app}"; Flags: ignoreversion

; Assets (icons, logos)
Source: "..\Source Code\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; Model Weights
Source: "..\..\Models\*"; DestDir: "{app}\Models"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; Launcher script
Source: "..\Source Code\Launch_HYPERLUMA.bat"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "HYPERLUMA Eye Disease Detection"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "HYPERLUMA Eye Disease Detection"; Tasks: startmenuicon
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenuicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} Application"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  if not IsWin64 then
  begin
    MsgBox('HYPERLUMA requires a 64-bit version of Windows 10 or later.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  Result := True;
end;
