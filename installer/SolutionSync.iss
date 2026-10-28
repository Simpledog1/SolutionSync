; Inno Setup script for the SolutionSync desktop app (built by scripts\build_desktop.ps1).
; Per-user install: no admin rights; user data in %APPDATA%\SolutionSync is never touched.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6A1C9F3E-2B7D-4E51-9C1A-5D2F8B7E4A90}
AppName=SolutionSync
AppVersion={#AppVersion}
AppPublisher=Simpledog1
AppPublisherURL=https://github.com/Simpledog1/SolutionSync
DefaultDirName={localappdata}\Programs\SolutionSync
DefaultGroupName=SolutionSync
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=SolutionSync-{#AppVersion}-setup
SetupIconFile=..\assets\solsync.ico
UninstallDisplayIcon={app}\SolutionSync.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "..\dist\SolutionSync\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\SolutionSync"; Filename: "{app}\SolutionSync.exe"
Name: "{userdesktop}\SolutionSync"; Filename: "{app}\SolutionSync.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SolutionSync.exe"; Description: "Open SolutionSync"; Flags: nowait postinstall skipifsilent
