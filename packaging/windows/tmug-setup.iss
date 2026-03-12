; tMUG - Tailscale Multi-platform User GUI
; Inno Setup Script
;
; This installer packages the PyInstaller-built standalone .exe.
; No Python or PyQt5 installation is required on the target machine.
;
; Build:
;   1. Run build-exe.sh (or PyInstaller directly) to create the .exe
;   2. Copy dist/tMUG-tailscale-manager.exe to this directory
;   3. Open this file in Inno Setup Compiler (iscc.exe) to produce the installer
;
; Copyright (c) DEC-LLC (Diwan Enterprise Consulting LLC)
; License: Apache-2.0

#define MyAppName "tMUG - Tailscale Multi-platform User GUI"
#define MyAppShortName "tMUG"
#define MyAppVersion "1.3.0"
#define MyAppPublisher "DEC-LLC (Diwan Enterprise Consulting LLC)"
#define MyAppURL "https://github.com/mvdiwan/tailscale-Multi-platfrom-User-GUI"
#define MyAppExeName "tMUG-tailscale-manager.exe"

[Setup]
AppId={{7A3B9C4D-5E6F-4A8B-9C0D-1E2F3A4B5C6D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppShortName}
DefaultGroupName={#MyAppShortName}
LicenseFile=..\..\LICENSE
OutputDir=output
OutputBaseFilename=tMUG-{#MyAppVersion}-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=tmug.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoCopyright=Copyright (c) DEC-LLC (Diwan Enterprise Consulting LLC)

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel2=This will install {#MyAppName} v{#MyAppVersion} on your computer.%n%nNo additional software (Python, etc.) is required. Everything is bundled in the application.

[Files]
Source: "tMUG-tailscale-manager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\tmug.svg"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "tmug.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppShortName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\tmug.ico"; Comment: "Launch tMUG Tailscale Manager"
Name: "{group}\Uninstall {#MyAppShortName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppShortName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\tmug.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent shellexec
