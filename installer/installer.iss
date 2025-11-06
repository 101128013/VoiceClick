; Inno Setup Installer Script for VoiceClick
; This script creates a Windows installer (.exe)
; Requires Inno Setup to be installed: https://jrsoftware.org/isinfo.php

#define AppName "VoiceClick"
#define AppVersion "1.0.0"
#define AppPublisher "VoiceClick Development Team"
#define AppURL "https://github.com/your-username/VoiceClick"
#define AppExeName "VoiceClick.exe"
#define SourceDir "..\dist"
#define OutputDir "..\dist\installer"

[Setup]
; App info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=
OutputDir={#OutputDir}
OutputBaseFilename=VoiceClick-Setup-v{#AppVersion}
SetupIconFile=..\src\resources\icons\voiceclick.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Start VoiceClick with Windows"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: startup

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel1.Caption := 'Welcome to VoiceClick Setup';
  WizardForm.WelcomeLabel2.Caption := 'This will install VoiceClick on your computer.' + #13#10 + #13#10 +
    'VoiceClick is a voice-to-text application that allows you to transcribe your speech directly into any text field.';
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
end;

