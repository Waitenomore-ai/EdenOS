; Eden's Garden branded NSIS welcome and completion pages.
; Uses the approved Eden character and the shared garden artwork.
; The standard NSIS directory and installation-progress pages remain native,
; so the installer keeps familiar Windows controls and accessibility.

!macro customWelcomePage
  !define MUI_WELCOMEPAGE_TITLE "Welcome to Eden's Garden Setup"
  !define MUI_WELCOMEPAGE_TEXT "This will install Eden's Garden on your computer.$\r$\n$\r$\nA safe, child-friendly space to learn, play, watch and grow at your own pace.$\r$\n$\r$\nChoose Next to select where Eden's Garden will be installed."
  !define MUI_WELCOMEPAGE_TITLE_3LINES
  !insertmacro MUI_PAGE_WELCOME
!macroend

!macro customFinishPage
  Function EdenStartApp
    ${if} ${isUpdated}
      StrCpy $1 "--updated"
    ${else}
      StrCpy $1 ""
    ${endif}
    ${StdUtils.ExecShellAsUser} $0 "$launchLink" "open" "$1"
  FunctionEnd

  !define MUI_FINISHPAGE_TITLE "Eden's Garden is ready!"
  !define MUI_FINISHPAGE_TEXT "Eden's Garden has been installed successfully.$\r$\n$\r$\nYour garden of learning, play and discovery is ready. Choose Finish to close Setup."
  !define MUI_FINISHPAGE_RUN
  !define MUI_FINISHPAGE_RUN_TEXT "Launch Eden's Garden now"
  !define MUI_FINISHPAGE_RUN_FUNCTION "EdenStartApp"
  !insertmacro MUI_PAGE_FINISH
!macroend
