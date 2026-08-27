; ============================================================
; VisionAI - Eye Disease Detection System
; SMART - Sanjivani Multidisciplinary AI Research & Technology
; setup.iss - Inno Setup Installer Script with Download & Install Options
; ============================================================

#define MyAppName "VisionAI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SMART - Sanjivani Multidisciplinary AI Research & Technology"
#define MyAppExeName "VisionAI.exe"
#define MyAppDescription "Professional Eye Disease Detection System"
#define GoogleDriveDownloadLink "https://drive.google.com/file/d/16Th-DtZp_cpYqrK4i-ykCmb9EuGfhXJ-/view?usp=drive_link"

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

[Types]
Name: "full"; Description: "Full Installation (App, _internal dependencies, and AI Models)"
Name: "portable"; Description: "Folder & App Launcher Package"
Name: "custom"; Description: "Custom Component Selection"; Flags: iscustom

[Components]
Name: "core"; Description: "VisionAI Core Application & _internal dependencies"; Types: full portable custom; Flags: fixed
Name: "models"; Description: "Pre-trained Neural Model Weights (Swin, EfficientNetV2, ResNeXt, FNet, Perceiver)"; Types: full custom
Name: "launcher"; Description: "Dual Folder & App Launcher Script (Launch_VisionAI.bat)"; Types: full portable custom
Name: "shortcuts"; Description: "Desktop & Start Menu Shortcuts"; Types: full portable custom

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop shortcut to launch VisionAI App directly"; GroupDescription: "Desktop Shortcuts:"; Components: shortcuts
Name: "foldericon"; Description: "Create a Desktop shortcut to Open VisionAI Folder & Launch App"; GroupDescription: "Desktop Shortcuts:"; Components: shortcuts
Name: "startmenuicon"; Description: "Create Start Menu shortcuts"; GroupDescription: "Start Menu Shortcuts:"; Components: shortcuts

[Dirs]
Name: "{app}"; Permissions: everyone-full
Name: "{app}\_internal"; Permissions: everyone-full
Name: "{app}\Models"; Permissions: everyone-full
Name: "{app}\assets"; Permissions: everyone-full
Name: "{app}\assets\icons"; Permissions: everyone-full
Name: "{app}\logs"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}\patients"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}\reports"; Permissions: everyone-full
Name: "{userappdata}\{#MyAppName}\snapshots"; Permissions: everyone-full

[Files]
; Main executable
Source: "dist\VisionAI\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Launcher batch script (opens folder and launches app)
Source: "..\Source Code\Launch_VisionAI.bat"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: launcher

; All PyInstaller bundled files (includes _internal folder)
Source: "dist\VisionAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Pre-trained model weights
Source: "..\..\Models\*"; DestDir: "{app}\Models"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist; Components: models
Source: "..\..\Models\*"; DestDir: "{app}\_internal\Models"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist; Components: models

; Assets (including logos and icons)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist; Components: core

; README
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme skipifsourcedoesntexist; Components: core

[Icons]
; Desktop shortcuts
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "VisionAI Eye Disease Detection System"; Tasks: desktopicon; Components: shortcuts
Name: "{autodesktop}\{#MyAppName} (Open Folder & App)"; Filename: "{app}\Launch_VisionAI.bat"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "Open VisionAI Folder & Launch App"; Tasks: foldericon; Components: shortcuts

; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "VisionAI Eye Disease Detection System"; Tasks: startmenuicon; Components: shortcuts
Name: "{group}\Open {#MyAppName} Folder & App"; Filename: "{app}\Launch_VisionAI.bat"; IconFilename: "{app}\assets\smartlab_logo.ico"; Comment: "Open VisionAI Folder & Launch App"; Tasks: startmenuicon; Components: shortcuts
Name: "{group}\Download Cloud Resources & Standalone Package"; Filename: "{#GoogleDriveDownloadLink}"; Comment: "Download latest VisionAI standalone packages"; Tasks: startmenuicon
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenuicon

[Registry]
; App registration
Root: HKLM; Subkey: "Software\SMART\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\SMART\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\SMART\{#MyAppName}"; ValueType: string; ValueName: "WeightsPath"; ValueData: "{app}\Models"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "PatientDataPath"; ValueData: "{userappdata}\{#MyAppName}\patients"; Flags: uninsdeletekey

[Run]
; Launch options after installation completes
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} Application"; Flags: nowait postinstall skipifsilent
Filename: "explorer.exe"; Parameters: """{app}"""; Description: "Open {#MyAppName} Installation Folder in File Explorer"; Flags: nowait postinstall unchecked
Filename: "{#GoogleDriveDownloadLink}"; Description: "Open Google Drive Cloud Download & Resource Folder"; Flags: shellexec nowait postinstall unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
var
  DownloadButton: TNewButton;

procedure OpenCloudDownloadLink(Sender: TObject);
var
  ErrorCode: Integer;
begin
  ShellExecute(0, 'open', '{#GoogleDriveDownloadLink}', '', '', SW_SHOWNORMAL);
end;

procedure InitializeWizard();
begin
  // Add a dedicated Download Cloud Package button to the Welcome Page
  DownloadButton := TNewButton.Create(WizardForm);
  DownloadButton.Parent := WizardForm.WelcomePage;
  DownloadButton.Left := ScaleX(20);
  DownloadButton.Top := ScaleY(270);
  DownloadButton.Width := ScaleX(240);
  DownloadButton.Height := ScaleY(30);
  DownloadButton.Caption := '☁️ Download Cloud Package (Google Drive)';
  DownloadButton.OnClick := @OpenCloudDownloadLink;
end;

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
    Result := True;
end;

// Initialize setup checks
function InitializeSetup(): Boolean;
begin
  if not IsWin64 then
  begin
    MsgBox('VisionAI requires a 64-bit version of Windows 10 or later.',
           mbError, MB_OK);
    Result := False;
    Exit;
  end;

  if not CheckDiskSpace() then
  begin
    Result := False;
    Exit;
  end;

  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('VisionAI has been installed successfully!' + #13#10 + #13#10 +
           'All runtime dependencies and _internal components have been installed in:' + #13#10 +
           ExpandConstant('{app}\') + #13#10 + #13#10 +
           'Desktop shortcuts created:' + #13#10 +
           '  - VisionAI (Direct App Launch)' + #13#10 +
           '  - VisionAI (Open Folder & App)',
           mbInformation, MB_OK);
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := MsgBox(
    'Are you sure you want to uninstall VisionAI?' + #13#10 +
    'Your patient data and reports will NOT be deleted.',
    mbConfirmation, MB_YESNO) = IDYES;
end;
