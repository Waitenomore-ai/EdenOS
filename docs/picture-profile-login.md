# Picture-based child sign-in proposal

Eden should let a child recognise their own account at the sign-in screen by
showing a large picture and display name. The child selects that tile, then
enters their own passphrase if one is required. The picture is a recognition
aid, not a password or authentication factor.

## Safety requirements

- Only an adult can choose or change the picture and display name.
- Built-in inclusive avatars should be available, with custom images optional.
- Pictures must be stored locally in a protected system directory, not inside a
  child's home folder and not in the public Desktop.
- The greeter must never show usernames, password hints, account status,
  recovery information, or another child's private data.
- A missing, invalid, or unreadable picture must fall back to a default avatar.
- The feature must work offline and must not upload or synchronise images.

## Accessibility requirements

- Tiles need large text, strong focus indication, keyboard navigation, touch and
  switch access, and screen-reader labels.
- Display names must remain readable at large text sizes and high contrast.
- Adults need a preview, reset, and remove action.
- The normal text-login fallback must remain available for every account.

Implementation is deliberately not enabled yet: the current image uses the
standard LightDM greeter, so the greeter integration and physical login flow
must be designed and tested before changing the installed iMac.

The source now includes a validation-only profile-card model for the future
greeter. It accepts only built-in avatar names and exposes only display name and
avatar to the public card view; the local username remains an internal account
mapping.

The source also includes a private local profile store for the future adult
setup flow. It validates records again on load, writes atomically with mode
`0600`, rejects duplicate accounts or unsafe avatars, and can remove one child
profile without changing the others. This is storage groundwork only; it does
not enable LightDM integration or claim physical iMac verification.
