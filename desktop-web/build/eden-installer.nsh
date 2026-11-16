; Eden's Garden branded NSIS welcome and completion pages.
; This is installation guidance, NOT a software licence agreement.
!macro customWelcomePage
  !define MUI_WELCOMEPAGE_TITLE "Welcome to Eden's Garden Setup"
  !define MUI_WELCOMEPAGE_TEXT "This will install Eden's Garden on your computer.$\r$\n$\r$\nA calm, child-friendly space to learn, play, watch and grow at your own pace.$\r$\n$\r$\nClick Next to choose your installation options."
  !insertmacro MUI_PAGE_WELCOME
!macroend

!macro customFinishPage
  !define MUI_FINISHPAGE_TITLE "Eden's Garden is ready!"
  !define MUI_FINISHPAGE_TEXT "Eden's Garden has been installed successfully.$\r$\n$\r$\nClick Finish to close Setup. You can launch Eden's Garden from your desktop or Start Menu."
  !insertmacro MUI_PAGE_FINISH
!macroend
