"""Adult-facing first-run child profile wizard."""

from __future__ import annotations

import sys
import threading

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, GLib, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian GTK runtime only
    raise SystemExit(
        "Eden setup needs the Debian GTK 4 runtime (python3-gi and gir1.2-gtk-4.0)."
    ) from exc

from .setup_model import ChildProfile, validate_child_profile
from .setup_service import create_child_account


class SetupWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden OS adult setup")
        self.set_default_size(760, 700)
        self.set_resizable(True)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        root.set_margin_top(30)
        root.set_margin_bottom(30)
        root.set_margin_start(36)
        root.set_margin_end(36)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(root)
        self.set_child(scroll)

        title = Gtk.Label(label="Create a child profile")
        title.add_css_class("eden-title")
        title.set_xalign(0)
        root.append(title)
        explanation = Gtk.Label(
            label=(
                "This makes a separate standard account for a child. "
                "It cannot install software or change adult settings. "
                "Eden keeps these details on this computer."
            )
        )
        explanation.set_wrap(True)
        explanation.set_xalign(0)
        root.append(explanation)

        self.nickname = self._add_entry(
            root, "Child nickname", "Name shown at the sign-in screen"
        )
        self.username = self._add_entry(
            root, "Sign-in username", "Use lowercase letters, numbers, _ or -"
        )
        self.password = self._add_entry(root, "Child passphrase", "At least 8 characters", password=True)
        self.confirmation = self._add_entry(
            root, "Type the passphrase again", "This checks that it matches", password=True
        )
        self.connect("close-request", self._close_during_setup)

        self.status = Gtk.Label(label="No profile has been created yet.")
        self.status.set_wrap(True)
        self.status.set_xalign(0)
        root.append(self.status)

        self.create_button = Gtk.Button(label="Create child profile")
        self.create_button.add_css_class("eden-small-button")
        self.create_button.connect("clicked", self._create_profile)
        root.append(self.create_button)

        note = Gtk.Label(
            label=(
                "Your adult account must approve this change. "
                "Eden does not save the passphrase."
            )
        )
        note.set_wrap(True)
        note.set_xalign(0)
        root.append(note)

    @staticmethod
    def _add_entry(
        parent: Gtk.Box, label: str, placeholder: str, password: bool = False
    ) -> Gtk.Entry:
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        caption = Gtk.Label(label=label)
        caption.set_xalign(0)
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)
        if password:
            entry.set_visibility(False)
            entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        row.append(caption)
        row.append(entry)
        parent.append(row)
        return entry

    def _create_profile(self, _button: Gtk.Button) -> None:
        try:
            profile = validate_child_profile(
                self.nickname.get_text(),
                self.username.get_text(),
                self.password.get_text(),
                self.confirmation.get_text(),
            )
        except ValueError as exc:
            self.status.set_label(str(exc))
            return

        password = self.password.get_text()
        self.password.set_text("")
        self.confirmation.set_text("")
        self.create_button.set_sensitive(False)
        self.status.set_label("Please approve the account setup and wait.")
        threading.Thread(
            target=self._create_profile_worker,
            args=(profile, password),
            daemon=False,
        ).start()

    def _create_profile_worker(self, profile: ChildProfile, password: str) -> None:
        try:
            create_child_account(profile.nickname, profile.username, password)
        except Exception:  # surface a plain-language failure; details are not logged
            GLib.idle_add(
                self._finish,
                False,
                "Setup did not finish. An adult administrator should check user accounts before retrying.",
            )
            return
        GLib.idle_add(
            self._finish,
            True,
            f"{profile.nickname}'s profile is ready. Select it at the sign-in screen to start Eden.",
        )

    def _finish(self, success: bool, message: str) -> bool:
        self.status.set_label(message)
        self.create_button.set_sensitive(True)
        if success:
            self.nickname.set_text("")
            self.username.set_text("")
        return GLib.SOURCE_REMOVE

    def _close_during_setup(self, _window: Gtk.Window) -> bool:
        if not self.create_button.get_sensitive():
            self.status.set_label("Please wait for the account setup to finish.")
            return True
        return False


class SetupApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id="uk.edenos.Setup",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self) -> None:
        window = self.props.active_window or SetupWindow(self)
        window.present()


def main() -> int:
    return SetupApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())

