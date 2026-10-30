# KidsTube browser pilot

## Selected service and status

The selected website is [KidsTube](https://www.kids-tube.com/), a hand-curated
video website that plays video through YouTube's privacy-enhanced player. The
child launcher and the account desktop now include a KidsTube shortcut. Firefox
ESR is configured with a system-wide allowlist, but the policy and playback have
not yet been checked in a built image. Treat this as a supervised development
pilot, not as a release-verified child-safe browser.

The site's own privacy notice says that, when used signed out, its host receives
technical connection data such as IP address and browser type. Its page offers
Google Analytics only with consent and names YouTube as the video provider.
Eden does not create a KidsTube account. Firefox is configured to clear browsing
data at shutdown and disable telemetry, studies, sync, and private developer
pages. Network services still receive ordinary connection data.

## Current policy

The Firefox policy is installed at `/etc/firefox/policies/policies.json` and
blocks all web URLs except these destinations:

- `kids-tube.com` and `www.kids-tube.com`
- YouTube's privacy-enhanced embed path on `youtube-nocookie.com`
- `ytimg.com` image hosts and `googlevideo.com` media hosts for embedded playback

`youtube.com` itself is not allowlisted. The embed and media-host exceptions are
broad: a child who obtains another YouTube embed or direct media URL may be able
to play it. This list does not prove that all playable content comes from
KidsTube's catalogue. The policy applies to Firefox for adult and child accounts
alike until Eden has a separately managed adult browser.

Firefox is also installed as a normal system application. Eden's launcher checks
the policy before opening its button, but a direct launch from another desktop
does not run that check first. Firefox should still load the root-owned system
policy; verify this from both launch paths. If the policy is missing or ignored,
do not let a child use the browser or an alternate desktop session.

## Required checks before unsupervised use

- Confirm Firefox reports the expected policies under `about:policies`.
- Launch Firefox directly from its system application entry and confirm the
  same policy is active; the Eden wrapper check does not cover this path.
- Confirm KidsTube loads and videos play; if it fails, add only the exact
  required host after review.
- Confirm direct `youtube.com`, search engines, arbitrary URLs, redirects,
  external links, downloads, `about:` pages, new windows, and new tabs are blocked
  or remain within the allowlist.
- Check the visible Firefox close control returns to Eden, and that opening the
  desktop shortcut uses the same system policy.
- Verify history, cookies, form data, and caches are cleared when Firefox exits.
- Test keyboard-only operation, touch, audio controls, reduced motion, and
  screen-reader support on actual target hardware.

Mozilla documents Firefox's WebsiteFilter block and exception lists, and its
system-wide `policies.json` location. These mechanisms are the basis for this
pilot; static configuration is not proof that every navigation path is blocked.
No filter can guarantee that every page or video is appropriate. Keep an adult
nearby and review the service and policy regularly.

## References

- [KidsTube about page](https://www.kids-tube.com/about)
- [KidsTube privacy notice](https://www.kids-tube.com/privacy)
- [Firefox WebsiteFilter policy](https://mozilla.github.io/policy-templates/#websitefilter)
- [Firefox policy configuration](https://support.mozilla.org/en-US/kb/customizing-firefox-using-policiesjson)


## Current release gate (supersedes pilot availability described above)

New images default `browser_enabled` to false. Both Eden launch paths require
that value to be exactly true AND browser_policy to be
`kidstube_allowlist_verified`, plus the existing strict Firefox-policy check.
Only an adult administrator can change the root-owned system defaults. Do not
mark the policy verified until the runtime checks above are documented. The
home button stays insensitive until that gate passes.

This controls the Eden button and wrapper. Firefox is still installed, so
alternate desktops and direct execution require separate testing/restriction;
this change does not establish an OS-wide browser security boundary.
