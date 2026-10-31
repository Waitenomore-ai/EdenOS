# First adult setup

An adult installs the test image and creates the adult administrator account in
the Debian installer. Eden does not ship a shared password or create a child
account before adult setup.

## Create a child profile

1. Sign in to the normal desktop with the adult administrator account.
2. Connect an existing writable backup destination and run `eden-backup
   /path/to/backup-folder` before creating the first profile.
3. Open **Eden Adult Setup** from the system applications menu.
4. Enter a nickname, a sign-in username, and a passphrase for the child. Eden
   does not ask for a birth date, email address, full name, or cloud account.
5. Approve the system account change in the PolicyKit prompt. The setup app is
   designed to create a separate standard account and set **Eden Child Session**
   as its preferred session. Verify the account type and session in the Debian
   graphical image before using this flow with a child.
6. Sign out and select the child's profile at LightDM. Confirm that the sign-in
   screen opens Eden for that profile; the adult can still sign in to the normal
   desktop.
7. The child has a KidsTube shortcut in Eden and in the account's Desktop folder.
   The restricted browser is an unverified development pilot; supervise its use
   and review `browser-safety.md`.

Picture-based child sign-in is planned but not enabled yet. The current build
uses the standard text-based LightDM login; see `picture-profile-login.md` for
the proposed safe design.

The current offline activity set is Tux Paint, Number Meadow, Word Woodland,
Story Garden, and Art Studio. The four Eden-native activities do not create
accounts, require network access, or save scores.

Eden keeps the profile nickname and local account on this computer. It does not
save the child's passphrase in a settings file. The setup source uses
AccountsService and PolicyKit for account changes. The account wizard,
authorization prompt, success path, and rollback still need image-level
verification.

## Session boundary

The child session has no desktop panel or adult settings entry. **Return to the
sign-in screen** ends the child session; LightDM requires credentials to enter
the adult account. KidsTube opens in a normal Firefox window with a visible close
control, and Alt+F4 is available from the window manager. The home screen also
has **Turn off computer**. It reminds the child to close activities and save
work, then asks systemd to power off. Verify this action and its adult-help error
message in the Debian image; Eden cannot save work inside another app for the
child.

The session choice is a usability boundary, not a security boundary against a
technically capable user or unsupervised physical access. LightDM may allow a
child to choose a different installed session; test the installed greeter and
account session behavior before deployment.

## Still to verify

- The account wizard and PolicyKit prompt need a Debian graphical image test.
- Verify AccountsService sets the Eden session for LightDM and the account is
  not an administrator.
- Verify failure and cancellation do not leave a usable partial account.
- Adult profile editing, deletion, multiple child profiles, and a guided
  accessibility setup flow are not implemented yet.

