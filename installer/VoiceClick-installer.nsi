; NSIS Installer Script for VoiceClick v1.0.0
; Task 18: Create NSIS installer script
; This script creates a Windows installer with uninstall support

;--------------------------------
; Includes
!include "MUI2.nsh"
!include "x64.nsh"

;--------------------------------
; Configuration

; Basic Info
Name "VoiceClick"
OutFile "VoiceClick-1.0.0-installer.exe"
InstallDir "$PROGRAMFILES\VoiceClick"
InstallDirRegKey HKLM "Software\VoiceClick" "Install_Dir"

; Request application privileges for Windows Vista and higher
RequestExecutionLevel admin

;--------------------------------
; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Language
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections

Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy main executable
  File "dist\VoiceClick.exe"
  
  ; Copy icon
  File "src\resources\icons\voiceclick.ico"
  
  ; Copy any required DLLs/libraries if needed
  ; File "dist\*.*"
  
  ; Create Start Menu shortcuts
  SetOutPath "$INSTDIR"
  CreateDirectory "$SMPROGRAMS\VoiceClick"
  CreateShortcut "$SMPROGRAMS\VoiceClick\VoiceClick.lnk" "$INSTDIR\VoiceClick.exe" "" "$INSTDIR\voiceclick.ico"
  CreateShortcut "$SMPROGRAMS\VoiceClick\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  ; Create Desktop shortcut
  CreateShortcut "$DESKTOP\VoiceClick.lnk" "$INSTDIR\VoiceClick.exe" "" "$INSTDIR\voiceclick.ico"
  
  ; Write registry entries
  WriteRegStr HKLM "Software\VoiceClick" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\VoiceClick" "Version" "1.0.0"
  
  ; Write uninstall registry entries
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceClick" "DisplayName" "VoiceClick"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceClick" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceClick" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceClick" "Publisher" "VoiceClick"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceClick" "DisplayIcon" "$INSTDIR\voiceclick.ico"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"
  ; Remove Start Menu shortcuts
  RMDir /r "$SMPROGRAMS\VoiceClick"
  
  ; Remove Desktop shortcut
  Delete "$DESKTOP\VoiceClick.lnk"
  
  ; Remove installed files
  Delete "$INSTDIR\VoiceClick.exe"
  Delete "$INSTDIR\voiceclick.ico"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remove installation directory if empty
  RMDir "$INSTDIR"
  
  ; Remove registry entries
  DeleteRegKey HKLM "Software\VoiceClick"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceClick"
SectionEnd

;--------------------------------
; Descriptions
LangString DESC_Install ${LANG_ENGLISH} "Install VoiceClick application"
LangString DESC_Uninstall ${LANG_ENGLISH} "Uninstall VoiceClick application"
