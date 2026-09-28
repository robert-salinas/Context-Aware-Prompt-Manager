#define AppName "RS Context Prompt Manager"
#define AppVersion "0.2.0"
#define AppPublisher "RS Digital"
#define AppExeName "RS-Context-Prompt-Manager.exe"

[Setup]
AppId={{9B96C64F-3D31-4E28-A716-21C26445FE52}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\RS-Prompt-Manager\app
DefaultGroupName=RS Digital
OutputDir=release
OutputBaseFilename=RS-Context-Prompt-Manager-Setup-{#AppVersion}
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
PrivilegesRequired=lowest
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\RS Prompt Manager"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\RS Context Prompt Manager"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent
