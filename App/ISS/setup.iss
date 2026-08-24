; Inno Setup Script for VisionAI Desktop Application
; SMART - Sanjivani Multidisciplinary AI Research & Technology

#define MyAppName "VisionAI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SMARTLAB-SU"
#define MyAppExeName "VisionAI.exe"

[Setup]
AppId={{D1A3F8B0-7C12-4E90-9A23-8B3E1F5C6D70}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\.exe
OutputBaseFilename=VisionAI_Setup_v1.0
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\Source Code\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs"
