!include "MUI2.nsh"
!define MUI_ICON "icon.ico"

Name "Warp Journal"
OutFile "warp-journal-1.0.0.exe"
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
  nsExec::Exec 'taskkill /f /im warp-journal.exe'

  ; Files to install
  File /r "warp-journal.dist\*.*"
;  File /r "warp-journal.dist\frontend*.*"
;  File "warp-journal.dist\icon.png"
;  File "warp-journal.dist\warp-journal.exe"
;
;  File /r "warp-journal.dist\tcl*.*"
;  File /r "warp-journal.dist\tk*.*"
;  File "warp-journal.dist\libcrypto-1_1.dll"
;  File "warp-journal.dist\libssl-1_1.dll"
;  File "warp-journal.dist\python310.dll"
;  File "warp-journal.dist\vcruntime140.dll"
;  File "warp-journal.dist\tcl86t.dll"
;  File "warp-journal.dist\tk86t.dll"
;  File "warp-journal.dist\sqlite3.dll"
;  File "warp-journal.dist\_bz2.pyd"
;  File "warp-journal.dist\_hashlib.pyd"
;  File "warp-journal.dist\_lzma.pyd"
;  File "warp-journal.dist\_socket.pyd"
;  File "warp-journal.dist\_ssl.pyd"
;  File "warp-journal.dist\_tkinter.pyd"
;  File "warp-journal.dist\_sqlite3.pyd"
;  File "warp-journal.dist\select.pyd"
;  File "warp-journal.dist\unicodedata.pyd"

  ; Write the installation path into the registry
  WriteRegStr HKLM "Software\WarpJournal" "InstallDir" "$INSTDIR"

  ; start menu shortcut
  CreateDirectory "$SMPROGRAMS\Warp Journal"
  CreateShortcut "$SMPROGRAMS\Warp Journal\Warp Journal.lnk" "$INSTDIR\warp-journal.exe"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WarpJournal" "DisplayName" "Warp Journal"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WarpJournal" "DisplayIcon" '"$INSTDIR\warp-journal.exe"'
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
