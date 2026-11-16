!ifndef BUILD_UNINSTALLER
; Eden's Garden illustrated NSIS pages using standard nsDialogs control ownership.
; Native directory and installation-progress pages remain familiar and accessible.
; All artwork uses approved Eden's Garden assets and the original approved Eden portrait.

; Resize the actual NSIS host window, not just the labels.
; Standard wizard pages share this host and its navigation buttons.
!define MUI_CUSTOMFUNCTION_GUIINIT EdenResizeWizard
Function EdenResizeWizard
  GetDlgItem $0 $HWNDPARENT 1
  System::Call 'user32::SetWindowPos(p r0, p 0, i 645, i 366, i 0, i 0, i 0x15) i .r9'
  GetDlgItem $0 $HWNDPARENT 2
  System::Call 'user32::SetWindowPos(p r0, p 0, i 560, i 366, i 0, i 0, i 0x15) i .r9'
  GetDlgItem $0 $HWNDPARENT 3
  System::Call 'user32::SetWindowPos(p r0, p 0, i 475, i 366, i 0, i 0, i 0x15) i .r9'
  ; Keep the top-left position, change the outer window to 750 x 450.
  System::Call 'user32::SetWindowPos(p $HWNDPARENT, p 0, i 0, i 0, i 750, i 450, i 0x16) i .r0'
FunctionEnd

Var EdenLaunchChoice
Var EdenOptionsLaunch
Var EdenFinishLaunch

!macro customInit
  StrCpy $EdenLaunchChoice "1"
!macroend

!macro customWelcomePage
  !insertmacro MUI_PAGE_INIT
  PageEx custom
    PageCallbacks EdenWelcomePre EdenWelcomeLeave
  PageExEnd

  Function EdenWelcomePre
    InitPluginsDir
    File /oname=$PLUGINSDIR\eden-welcome.bmp "${BUILD_RESOURCES_DIR}\installer-welcome.bmp"
    nsDialogs::Create 1044
    Pop $0
    ; Resize the real page dialog to occupy the enlarged host client area.
    System::Call 'user32::SetWindowPos(p r0, p 0, i 0, i 0, i 734, i 300, i 0x16) i .r9'
    ${NSD_CreateBitmap} 0u 0u 550u 215u ""
    Pop $1
    ${NSD_SetImage} $1 "$PLUGINSDIR\eden-welcome.bmp" $2
    System::Call 'user32::SetWindowPos(p r1, p 0, i 0, i 0, i 734, i 300, i 0x16) i .r9'

    ; Heading and explanatory text are rendered directly into the BMP.


    ; HWND_BOTTOM=1, SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE=0x13
    ; Keep the illustrated background behind text and interactive controls.
    System::Call 'user32::SetWindowPos(p r1, p 1, i 0, i 0, i 0, i 0, i 0x13) i .r0'
    nsDialogs::Show
  FunctionEnd

  Function EdenWelcomeLeave
  FunctionEnd
!macroend

!macro customPageAfterChangeDir
  !insertmacro MUI_PAGE_INIT
  PageEx custom
    PageCallbacks EdenOptionsPre EdenOptionsLeave
  PageExEnd

  Function EdenOptionsPre
    InitPluginsDir
    File /oname=$PLUGINSDIR\eden-options.bmp "${BUILD_RESOURCES_DIR}\installer-options.bmp"
    nsDialogs::Create 1044
    Pop $0
    ; Resize the real page dialog to occupy the enlarged host client area.
    System::Call 'user32::SetWindowPos(p r0, p 0, i 0, i 0, i 734, i 300, i 0x16) i .r9'
    ${NSD_CreateBitmap} 0u 0u 550u 215u ""
    Pop $1
    ${NSD_SetImage} $1 "$PLUGINSDIR\eden-options.bmp" $2
    System::Call 'user32::SetWindowPos(p r1, p 0, i 0, i 0, i 734, i 300, i 0x16) i .r9'

    ; Heading and explanatory text are rendered directly into the BMP.


    ${NSD_CreateCheckBox} 140u 151u 260u 16u "Launch Eden's Garden after setup"
    Pop $EdenOptionsLaunch
    SetCtlColors $EdenOptionsLaunch "24344A" "FFFFFF"
    ${If} $EdenLaunchChoice == "1"
      SendMessage $EdenOptionsLaunch ${BM_SETCHECK} ${BST_CHECKED} 0
    ${EndIf}

    ; HWND_BOTTOM=1, SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE=0x13
    ; Keep the illustrated background behind text and interactive controls.
    System::Call 'user32::SetWindowPos(p r1, p 1, i 0, i 0, i 0, i 0, i 0x13) i .r0'
    nsDialogs::Show
  FunctionEnd

  Function EdenOptionsLeave
    SendMessage $EdenOptionsLaunch ${BM_GETCHECK} 0 0 $0
    ${If} $0 == ${BST_CHECKED}
      StrCpy $EdenLaunchChoice "1"
    ${Else}
      StrCpy $EdenLaunchChoice "0"
    ${EndIf}
  FunctionEnd
!macroend

!macro customFinishPage
  !insertmacro MUI_PAGE_INIT
  PageEx custom
    PageCallbacks EdenFinishPre EdenFinishLeave
  PageExEnd

  Function EdenFinishPre
    InitPluginsDir
    File /oname=$PLUGINSDIR\eden-finish.bmp "${BUILD_RESOURCES_DIR}\installer-finish.bmp"
    nsDialogs::Create 1044
    Pop $0
    ; Resize the real page dialog to occupy the enlarged host client area.
    System::Call 'user32::SetWindowPos(p r0, p 0, i 0, i 0, i 734, i 300, i 0x16) i .r9'
    ${NSD_CreateBitmap} 0u 0u 550u 215u ""
    Pop $1
    ${NSD_SetImage} $1 "$PLUGINSDIR\eden-finish.bmp" $2
    System::Call 'user32::SetWindowPos(p r1, p 0, i 0, i 0, i 734, i 300, i 0x16) i .r9'

    ; Heading and explanatory text are rendered directly into the BMP.


    ${NSD_CreateCheckBox} 140u 153u 260u 16u "Launch Eden's Garden now"
    Pop $EdenFinishLaunch
    SetCtlColors $EdenFinishLaunch "24344A" "FFFFFF"
    ${If} $EdenLaunchChoice == "1"
      SendMessage $EdenFinishLaunch ${BM_SETCHECK} ${BST_CHECKED} 0
    ${EndIf}

    ; HWND_BOTTOM=1, SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE=0x13
    ; Keep the illustrated background behind text and interactive controls.
    System::Call 'user32::SetWindowPos(p r1, p 1, i 0, i 0, i 0, i 0, i 0x13) i .r0'
    nsDialogs::Show
  FunctionEnd

  Function EdenStartApp
    ${if} ${isUpdated}
      StrCpy $1 "--updated"
    ${else}
      StrCpy $1 ""
    ${endif}
    ${StdUtils.ExecShellAsUser} $0 "$launchLink" "open" "$1"
  FunctionEnd

  Function EdenFinishLeave
    SendMessage $EdenFinishLaunch ${BM_GETCHECK} 0 0 $0
    ${If} $0 == ${BST_CHECKED}
      Call EdenStartApp
    ${EndIf}
  FunctionEnd
!macroend

!endif ; !ifndef BUILD_UNINSTALLER
