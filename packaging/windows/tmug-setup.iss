; tMUG - Tailscale Multi-platform User GUI
; Inno Setup Script
;
; Prerequisites: Python 3.x and PyQt5 must be installed on the target system.
; Build: Open this file in Inno Setup Compiler (iscc.exe) on Windows to produce the installer.
;
; Copyright (c) DEC-LLC (Diwan Enterprise Consulting LLC)
; License: Apache-2.0

#define MyAppName "tMUG - Tailscale Multi-platform User GUI"
#define MyAppShortName "tMUG"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "DEC-LLC (Diwan Enterprise Consulting LLC)"
#define MyAppURL "https://github.com/mvdiwan/tailscale-Multi-platfrom-User-GUI"
#define MyAppExeName "tMUG-tailscale-manager.bat"

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
SetupIconFile=..\..\tmug.svg
UninstallDisplayIcon={app}\tmug.svg
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoCopyright=Copyright (c) DEC-LLC (Diwan Enterprise Consulting LLC)

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel2=This will install {#MyAppName} v{#MyAppVersion} on your computer.%n%nNote: Python 3 and PyQt5 must already be installed. If you do not have them, install Python from python.org and run:%n%n  pip install PyQt5%n%nbefore using tMUG.

[Files]
Source: "..\..\cross-platform\tailscale_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\cross-platform\setup.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\tmug.svg"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "tMUG-tailscale-manager.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppShortName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\tmug.svg"; Comment: "Launch tMUG Tailscale Manager"
Name: "{group}\Uninstall {#MyAppShortName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppShortName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\tmug.svg"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent shellexec

[Code]
function IsPythonInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
  if not Result then
    Result := Exec('cmd.exe', '/c python3 --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function InitializeSetup: Boolean;
begin
  Result := True;
  if not IsPythonInstalled then
  begin
    if MsgBox('Python 3 does not appear to be installed or is not in PATH.' + #13#10 + #13#10 +
              'tMUG requires Python 3 and PyQt5 to run.' + #13#10 +
              'Install Python from https://www.python.org/downloads/' + #13#10 + #13#10 +
              'Continue installation anyway?',
              mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;
