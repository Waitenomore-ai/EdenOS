!ifndef BUILD_UNINSTALLER
; Eden's Garden illustrated NSIS pages using standard nsDialogs control ownership.
; Native directory and installation-progress pages remain familiar and accessible.
; All artwork uses approved Eden's Garden assets and the original approved Eden portrait.

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
    ${NSD_CreateBitmap} 0u 0u 417u 193u ""
    Pop $1
    ${NSD_SetImage} $1 "$PLUGINSDIR\eden-welcome.bmp" $2

    ${NSD_CreateLabel} 140u 72u 154u 27u "Welcome to Eden's Garden"
    Pop $3
    SetCtlColors $3 "10223F" "FFFFFF"
    CreateFont $4 "Segoe UI" "11" "700"
    SendMessage $3 ${WM_SETFONT} $4 0

    ${NSD_CreateLabel} 140u 107u 154u 53u "This will install Eden's Garden on your computer.$\r$\nA calm, child-friendly space to learn, play,$\r$\nwatch and grow at your own pace."
    Pop $5
    SetCtlColors $5 "24344A" "FFFFFF"

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
    ${NSD_CreateBitmap} 0u 0u 417u 193u ""
    Pop $1
    ${NSD_SetImage} $1 "$PLUGINSDIR\eden-options.bmp" $2

    ${NSD_CreateLabel} 140u 72u 154u 27u "Choose Installation Options"
    Pop $3
    SetCtlColors $3 "10223F" "FFFFFF"
    CreateFont $4 "Segoe UI" "11" "700"
    SendMessage $3 ${WM_SETFONT} $4 0

    ${NSD_CreateLabel} 140u 106u 154u 38u "Desktop and Start Menu shortcuts are included.$\r$\nChoose whether to open Eden after setup."
    Pop $5
    SetCtlColors $5 "24344A" "FFFFFF"

    ${NSD_CreateCheckBox} 140u 151u 154u 16u "Launch Eden's Garden after setup"
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
    ${NSD_CreateBitmap} 0u 0u 417u 193u ""
    Pop $1
    ${NSD_SetImage} $1 "$PLUGINSDIR\eden-finish.bmp" $2

    ${NSD_CreateLabel} 140u 72u 154u 27u "Installation complete!"
    Pop $3
    SetCtlColors $3 "10223F" "FFFFFF"
    CreateFont $4 "Segoe UI" "11" "700"
    SendMessage $3 ${WM_SETFONT} $4 0

    ${NSD_CreateLabel} 140u 105u 154u 42u "Eden's Garden has been installed successfully.$\r$\nYour garden of learning and discovery is ready."
    Pop $5
    SetCtlColors $5 "24344A" "FFFFFF"

    ${NSD_CreateCheckBox} 140u 153u 154u 16u "Launch Eden's Garden now"
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
