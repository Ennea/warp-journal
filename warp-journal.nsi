!include "MUI2.nsh"
!define MUI_ICON "icon.ico"

Name "Warp Journal"
OutFile "dist\warp-journal-1.2.0.exe"
Unicode True
RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\Warp Journal"
InstallDirRegKey HKLM "Software\WarpJournal" "InstallDir"

;--------------------------------
; Pages

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Section

Section "Warp Journal"

  SectionIn RO
  SetOutPath $INSTDIR

  ; Kill Warp Journal if it's already running
  nsExec::Exec 'taskkill /f /im warp_journal.exe'

  ; Files to install
  File /r "warp_journal.dist\*.*"

  ; Write the installation path into the registry
  WriteRegStr HKLM "Software\WarpJournal" "InstallDir" "$INSTDIR"

  ; start menu shortcut
  CreateDirectory "$SMPROGRAMS\Warp Journal"
  CreateShortcut "$SMPROGRAMS\Warp Journal\Warp Journal.lnk" "$INSTDIR\warp_journal.exe"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WarpJournal" "DisplayName" "Warp Journal"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WarpJournal" "DisplayIcon" '"$INSTDIR\warp_journal.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WarpJournal" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WarpJournal" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WarpJournal" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

;--------------------------------
; Uninstaller

Section "Uninstall"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WarpJournal"
  DeleteRegKey HKLM "Software\WarpJournal"

  Delete "$SMPROGRAMS\Warp Journal\*.lnk"
  RMDir "$SMPROGRAMS\Warp Journal"
  RMDir /r "$INSTDIR"

SectionEnd
