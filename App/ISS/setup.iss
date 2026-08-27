; ============================================================
; VisionAI - Eye Disease Detection System
; SMART - Sanjivani Multidisciplinary AI Research & Technology
; setup.iss - Inno Setup Installer Script
; ============================================================

#define MyAppName "VisionAI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SMART - Sanjivani Multidisciplinary AI Research & Technology"
#define MyAppExeName "VisionAI.exe"
#define MyAppDescription "Professional Eye Disease Detection System"

[Setup]
AppId={{B2C3D4E5-F6A7-8901-BCDE-F12345678901}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://sanjivani.edu.in
AppSupportURL=https://sanjivani.edu.in/support
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=no
OutputDir=Output
OutputBaseFilename=VisionAI_Setup_v1.0.0
SetupIconFile=assets\smartlab_logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0.19041
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Additional icons:"

[Dirs]
Name: "{app}"; Permissions: everyone-full
Name: "{app}\weights"; Permissions: everyone-full
Name: "{app}\assets"; Permissions: everyone-full
Name: "{app}\assets\icons"; Permissions: everyone-full
Name: "{app}\logs"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}\patients"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}\reports"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}\snapshots"; Permissions: everyone-full

[Files]
; Main executable
Source: "dist\VisionAI\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Launcher batch script (opens folder and launches app)
Source: "..\Source Code\Launch_VisionAI.bat"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; All PyInstaller bundled files (includes weights)
Source: "dist\VisionAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Assets (including logos and icons)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; README
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme skipifsourcedoesntexist

[Icons]
; Desktop shortcuts
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "Eye Disease Detection System App"; Tasks: desktopicon
Name: "{autodesktop}\{#MyAppName} (Open Folder & App)"; Filename: "{app}\Launch_VisionAI.bat"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "Open VisionAI Folder & Launch App"; Tasks: desktopicon

; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "Eye Disease Detection System"; Tasks: startmenuicon
Name: "{group}\Open {#MyAppName} Folder & App"; Filename: "{app}\Launch_VisionAI.bat"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "Open VisionAI Folder & Launch App"; Tasks: startmenuicon
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenuicon

[Registry]
; App registration
Root: HKLM; Subkey: "Software\SMART\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\SMART\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\SMART\{#MyAppName}"; ValueType: string; ValueName: "WeightsPath"; ValueData: "{app}\weights"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "PatientDataPath"; ValueData: "{userappdata}\{#MyAppName}\patients"; Flags: uninsdeletekey

[Run]
; Launch options after install
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} application"; Flags: nowait postinstall skipifsilent
Filename: "explorer.exe"; Parameters: """{app}"""; Description: "Open {#MyAppName} installation folder"; Flags: nowait postinstall unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
function CheckDiskSpace(): Boolean;
var
  freeSpace, totalSpace: Int64;
begin
  if GetSpaceOnDisk64(ExpandConstant('{autopf}'), freeSpace, totalSpace) then
  begin
    if freeSpace < 1073741824 then
    begin
      MsgBox('Insufficient disk space.' + #13#10 +
             'VisionAI requires at least 1 GB of free space.' + #13#10 +
             'Please free up space and try again.',
             mbError, MB_OK);
      Result := False;
    end
    else
      Result := True;
  end
  else
    Result := True; // Proceed if disk space check itself fails
end;

// Initialize setup checks
function InitializeSetup(): Boolean;
begin
  // Check 64-bit Windows
  if not IsWin64 then
  begin
    MsgBox('VisionAI requires a 64-bit version of Windows 10 or later.',
           mbError, MB_OK);
    Result := False;
    Exit;
  end;

  // Check disk space
  if not CheckDiskSpace() then
  begin
    Result := False;
    Exit;
  end;

  Result := True;
end;

// Post install message
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('VisionAI has been installed successfully!' + #13#10 + #13#10 +
           'IMPORTANT: Make sure your trained model weight files' + #13#10 +
           '(.pth files) are placed in:' + #13#10 + #13#10 +
           ExpandConstant('{app}\weights\') + #13#10 + #13#10 +
           'Required weight files:' + #13#10 +
           '  - swin_scratch_best.pth' + #13#10 +
           '  - efficientnetv2s_scratch_best.pth' + #13#10 +
           '  - resnext50_scratch_best.pth' + #13#10 +
           '  - fnet_scratch_best.pth' + #13#10 +
           '  - perceiver_scratch_best.pth',
           mbInformation, MB_OK);
  end;
end;

// Confirm uninstall
function InitializeUninstall(): Boolean;
begin
  Result := MsgBox(
    'Are you sure you want to uninstall VisionAI?' + #13#10 +
    'Your patient data and reports will NOT be deleted.',
    mbConfirmation, MB_YESNO) = IDYES;
end;
