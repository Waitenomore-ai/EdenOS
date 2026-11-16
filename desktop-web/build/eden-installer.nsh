!ifndef BUILD_UNINSTALLER
; Eden's Garden illustrated, full-width NSIS pages.
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
  !insertmacro MUI_PAGE_FUNCTION_FULLWINDOW
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

    ${NSD_CreateLabel} 205u 119u 202u 27u "Welcome to the Eden's Garden Setup"
    Pop $3
    SetCtlColors $3 "10223F" "FFFFFF"
    CreateFont $4 "Segoe UI" "15" "700"
    SendMessage $3 ${WM_SETFONT} $4 0

    ${NSD_CreateLabel} 205u 151u 202u 34u "This will install Eden's Garden on your computer.$\r$\nA calm, child-friendly space to learn, play,$\r$\nwatch and grow at your own pace."
    Pop $5
    SetCtlColors $5 "24344A" "FFFFFF"

    Call muiPageLoadFullWindow
    nsDialogs::Show
    Call muiPageUnloadFullWindow
  FunctionEnd

  Function EdenWelcomeLeave
  FunctionEnd
!macroend

!macro customPageAfterChangeDir
  !insertmacro MUI_PAGE_INIT
  !insertmacro MUI_PAGE_FUNCTION_FULLWINDOW
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

    ${NSD_CreateLabel} 205u 119u 202u 27u "Choose Installation Options"
    Pop $3
    SetCtlColors $3 "10223F" "FFFFFF"
    CreateFont $4 "Segoe UI" "15" "700"
    SendMessage $3 ${WM_SETFONT} $4 0

    ${NSD_CreateLabel} 205u 149u 202u 29u "A desktop shortcut and Start Menu entry$\r$\nwill be created for easy access."
    Pop $5
    SetCtlColors $5 "24344A" "FFFFFF"

    ${NSD_CreateCheckBox} 205u 177u 205u 16u "Launch Eden's Garden after setup"
    Pop $EdenOptionsLaunch
    SetCtlColors $EdenOptionsLaunch "24344A" "FFFFFF"
    ${If} $EdenLaunchChoice == "1"
      SendMessage $EdenOptionsLaunch ${BM_SETCHECK} ${BST_CHECKED} 0
    ${EndIf}

    Call muiPageLoadFullWindow
    nsDialogs::Show
    Call muiPageUnloadFullWindow
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
  !insertmacro MUI_PAGE_FUNCTION_FULLWINDOW
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

    ${NSD_CreateLabel} 205u 119u 202u 27u "Eden's Garden is ready!"
    Pop $3
    SetCtlColors $3 "10223F" "FFFFFF"
    CreateFont $4 "Segoe UI" "16" "700"
    SendMessage $3 ${WM_SETFONT} $4 0

    ${NSD_CreateLabel} 205u 151u 202u 28u "Eden's Garden has been installed successfully.$\r$\nYour garden of learning and discovery is ready."
    Pop $5
    SetCtlColors $5 "24344A" "FFFFFF"

    ${NSD_CreateCheckBox} 205u 179u 205u 15u "Launch Eden's Garden now"
    Pop $EdenFinishLaunch
    SetCtlColors $EdenFinishLaunch "24344A" "FFFFFF"
    ${If} $EdenLaunchChoice == "1"
      SendMessage $EdenFinishLaunch ${BM_SETCHECK} ${BST_CHECKED} 0
    ${EndIf}

    Call muiPageLoadFullWindow
    nsDialogs::Show
    Call muiPageUnloadFullWindow
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
