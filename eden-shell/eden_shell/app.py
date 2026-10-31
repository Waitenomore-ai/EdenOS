"""GTK 4 child-facing Eden OS launcher."""

from __future__ import annotations

import getpass
import sys
import threading
from datetime import date
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, GLib, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - requires Debian GTK runtime
    raise SystemExit(
        "Eden OS needs the Debian GTK 4 runtime (python3-gi and gir1.2-gtk-4.0)."
    ) from exc

from .catalogue import CATEGORIES, Activity, load_catalogue
from .browser import browser_access_ready
from .version import build_label
from .navigation import ScreenState
from .launch_control import LaunchCooldown
from .preferences import (
    AccessibilityPreferences,
    accessibility_preset,
    load_preferences,
    save_preferences,
)


class EdenWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden OS")
        self.set_default_size(1024, 768)
        self.fullscreen()
        self.state = ScreenState()
        self.catalogue = load_catalogue()
        self._launch_cooldown = LaunchCooldown()
        self.preferences = load_preferences()
        self._install_styles()
        self._apply_preferences()
        self._render()
        self._page_focus_target.grab_focus()

    def _install_styles(self) -> None:
        provider = Gtk.CssProvider()
        css_path = Path(__file__).parent / "data" / "eden.css"
        provider.load_from_path(str(css_path))
        display = self.get_display()
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self._css_provider = provider

    def _apply_preferences(self) -> None:
        scale = self.preferences.text_scale
        scaled_css = "\n".join(
            (
                f"* {{ font-size: {round(18 * scale)}px; }}",
                f".eden-title {{ font-size: {round(34 * scale)}px; }}",
                f".eden-subtitle {{ font-size: {round(21 * scale)}px; }}",
                f".eden-card-label {{ font-size: {round(25 * scale)}px; }}",
                f".eden-small-button {{ font-size: {round(20 * scale)}px; }}",
                f".eden-empty {{ font-size: {round(21 * scale)}px; }}",
                f".eden-status {{ font-size: {round(18 * scale)}px; }}",
            )
        )
        provider = Gtk.CssProvider()
        provider.load_from_data(scaled_css.encode("utf-8"))
        if hasattr(self, "_scale_provider"):
            Gtk.StyleContext.remove_provider_for_display(
                self.get_display(), self._scale_provider
            )
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        self._scale_provider = provider
        if self.preferences.high_contrast:
            self.add_css_class("contrast")
        else:
            self.remove_css_class("contrast")
        if self.preferences.reduced_motion:
            self.add_css_class("reduced-motion")
        else:
            self.remove_css_class("reduced-motion")

    def _accessible_button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button()
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.add_css_class("eden-small-button")
        button.connect("clicked", callback)
        return button

    def _text_button(self, label: str, callback) -> Gtk.Button:
        button = self._accessible_button(label, callback)
        button.set_label(label)
        return button

    def _tile(self, label: str, icon_name: str, callback) -> Gtk.Button:
        button = Gtk.Button()
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.add_css_class("eden-card")
        button.connect("clicked", callback)
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        content.set_halign(Gtk.Align.CENTER)
        icon_path = Path(__file__).parent / "data" / "icons" / f"{icon_name}.svg"
        image = Gtk.Image.new_from_file(str(icon_path))
        image.set_pixel_size(36)
        image.set_focusable(False)
        content.append(image)
        title = Gtk.Label(label=label)
        title.add_css_class("eden-card-label")
        content.append(title)
        button.set_child(content)
        return button

    def _render(self) -> None:
        self._status_label = None
        self._page_focus_target = None
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(22)
        root.set_margin_bottom(22)
        root.set_margin_start(28)
        root.set_margin_end(28)
        # A real GTK picture layer keeps the enchanted garden visible
        # behind compact navigation controls. High contrast stays opaque.
        backdrop = Gtk.Overlay()
        if not self.preferences.high_contrast:
            gallery = Path("/usr/share/backgrounds/edenos/daily")
            daily_images = sorted(gallery.glob("*.png")) if gallery.is_dir() else []
            wallpaper_path = (
                daily_images[date.today().toordinal() % len(daily_images)]
                if daily_images
                else Path("/usr/share/backgrounds/edenos/01-eden-sunrise.png")
            )
            if wallpaper_path.is_file():
                backdrop_image = Gtk.Picture.new_for_filename(str(wallpaper_path))
                backdrop_image.set_content_fit(Gtk.ContentFit.COVER)
                backdrop.set_child(backdrop_image)
        backdrop.add_overlay(root)
        self.set_child(backdrop)
        self._root_container = root

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        if self.state.page != "home":
            home_button = self._text_button("Home", self._go_home)
            header.append(home_button)
            self._page_focus_target = home_button
        logo_path = Path("/usr/share/eden-os/branding/eden-logo.png")
        if not logo_path.is_file():
            logo_path = Path("/usr/share/pixmaps/edenos-logo.png")
        if logo_path.is_file():
            logo = Gtk.Image.new_from_file(str(logo_path))
            logo.set_pixel_size(200)
            logo.set_tooltip_text("Eden OS")
            header.append(logo)
        header_spacer = Gtk.Box()
        header_spacer.set_hexpand(True)
        header.append(header_spacer)
        settings_button = self._text_button("Settings ⚙", self._open_settings)
        settings_button.add_css_class("eden-header-control")
        header.append(settings_button)
        root.append(header)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        root.append(scroll)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=22)
        content.add_css_class("eden-content")
        scroll.set_child(content)

        if self.state.page == "home":
            self._render_home(content)
        elif self.state.page == "category":
            self._render_category(content)
        elif self.state.page == "progress":
            self._render_progress(content)
        elif self.state.page == "help":
            self._render_help(content)
        else:
            self._render_settings(content)

    def _render_home(self, content: Gtk.Box) -> None:
        welcome = Gtk.Label(label=f"Hello, {getpass.getuser()}!")
        welcome.add_css_class("eden-welcome")
        welcome.set_xalign(0)
        content.append(welcome)
        prompt = Gtk.Label(label="What would you like to do today?")
        prompt.add_css_class("eden-home-prompt")
        prompt.set_xalign(0)
        content.append(prompt)

        # Keep every shortcut functional. Picture assets are decoration, never hit targets.
        # Network features remain disabled until adult-reviewed policy is verified.
        actions = [
            ("Learn", "learn", self._open_category("learn"), True, "number-meadow"),
            ("Play Games", "play", self._open_category("play"), True, "puzzle-pond"),
            ("Create", "create", self._open_category("create"), True, "art-studio"),
            ("Read", "read", self._open_category("read"), True, "story-garden"),
            ("Number Meadow", "numbers", self._open_named_activity("number-meadow"), True, "number-meadow"),
            ("Word Woodland", "words", self._open_named_activity("word-woodland"), True, "word-woodland"),
            ("Puzzle Pond", "puzzles", self._open_named_activity("puzzle-pond"), True, "puzzle-pond"),
            ("Art Studio", "studio", self._open_named_activity("art-studio"), True, "art-studio"),
            ("Explore", "explore", self._open_category("read"), True, "nature-explorer"),
            ("My Stuff", "stuff", self._open_progress, True, "time-routines"),
            ("Settings", "settings", self._open_settings, True, "feelings-quiet-space"),
            ("Help", "help", self._open_help, True, "story-garden"),
        ]
        grid = Gtk.Grid(column_spacing=16, row_spacing=17)
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)
        grid.add_css_class("eden-dashboard-grid")
        for index, (label, style, action, enabled, illustration) in enumerate(actions):
            button = self._accessible_button(label, action)
            button.add_css_class("eden-home-button")
            button.add_css_class("eden-" + style)
            button.set_size_request(212, 94)
            picture_path = Path(__file__).parent / "data" / "activity-art" / (illustration + ".svg")
            if picture_path.is_file() and not self.preferences.high_contrast:
                body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=9)
                body.set_halign(Gtk.Align.CENTER)
                body.set_valign(Gtk.Align.CENTER)
                icon = Gtk.Image.new_from_file(str(picture_path))
                icon.set_pixel_size(74)
                body.append(icon)
                name = Gtk.Label(label=label)
                name.set_wrap(True)
                name.set_max_width_chars(12)
                name.set_justify(Gtk.Justification.CENTER)
                name.add_css_class("eden-home-label")
                body.append(name)
                button.set_child(body)
            else:
                button.set_label(label)
            button.set_sensitive(enabled)
            grid.attach(button, index % 4, index // 4, 1, 1)
            if self._page_focus_target is None and enabled:
                self._page_focus_target = button
        content.append(grid)

    def _open_named_activity(self, activity_id: str):
        def open_activity(_button: Gtk.Button) -> None:
            activity = next((item for item in self.catalogue if item.id == activity_id), None)
            if activity is None:
                self._show_status("Ask an adult to add this game.")
                return
            self._launch_activity(activity)
        return open_activity

    def _render_category(self, content: Gtk.Box) -> None:
        category = next(item for item in CATEGORIES if item.slug == self.state.category)
        title = Gtk.Label(label=category.label)
        title.add_css_class("eden-wooden-heading")
        title.set_halign(Gtk.Align.CENTER)
        title.set_xalign(0.5)
        content.append(title)
        activities = [item for item in self.catalogue if item.category == category.slug]
        if not activities:
            self._append_empty(content, "Your adult can add activities here.")
            return
        activity_grid = Gtk.Grid(column_spacing=16, row_spacing=16)
        activity_grid.set_halign(Gtk.Align.CENTER)
        for index, activity in enumerate(activities):
            activity_grid.attach(self._activity_tile(activity), index % 3, index // 3, 1, 1)
        content.append(activity_grid)

    def _activity_tile(self, activity: Activity) -> Gtk.Button:
        button = self._accessible_button(
            f"Open {activity.title}", lambda _button: self._launch_activity(activity)
        )
        button.add_css_class("eden-activity-tile")
        button.set_size_request(230, 210)
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        body.set_halign(Gtk.Align.CENTER)
        body.set_valign(Gtk.Align.CENTER)
        icon_path = Path(__file__).parent / "data" / "activity-art" / f"{activity.id}.svg"
        if icon_path.is_file():
            picture = Gtk.Picture.new_for_filename(str(icon_path))
            picture.set_content_fit(Gtk.ContentFit.CONTAIN)
            picture.set_size_request(120, 105)
            body.append(picture)
        title = Gtk.Label(label=activity.title)
        title.add_css_class("eden-card-label")
        title.set_wrap(True)
        title.set_justify(Gtk.Justification.CENTER)
        body.append(title)
        button.set_child(body)
        return button

    def _append_activity(self, content: Gtk.Box, activity: Activity) -> None:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        row.add_css_class("eden-empty")
        details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        details.set_hexpand(True)
        title = Gtk.Label(label=activity.title)
        title.add_css_class("eden-card-label")
        title.set_xalign(0)
        description = Gtk.Label(label=activity.description)
        description.add_css_class("eden-status")
        description.set_xalign(0)
        description.set_wrap(True)
        details.append(title)
        details.append(description)
        row.append(details)
        button = self._text_button(
            "Open activity", lambda _button: self._launch_activity(activity)
        )
        row.append(button)
        content.append(row)

    def _launch_activity(self, activity: Activity) -> None:
        try:
            app_info = Gio.DesktopAppInfo.new(activity.desktop_id)
        except (TypeError, GLib.Error):
            app_info = None
        if app_info is None:
            self._show_status("I couldn't open that activity. Ask an adult for help.")
            return
        if not self._launch_cooldown.try_start(activity.id):
            self._show_status("Please give that activity a moment to open.")
            return
        try:
            app_info.launch([], None)
        except GLib.Error:  # pragma: no cover - actual desktop launch requires GTK session
            self._launch_cooldown.release(activity.id)
            self._show_status("I couldn't open that activity. Ask an adult for help.")

    def _render_progress(self, content: Gtk.Box) -> None:
        title = Gtk.Label(label="My Progress")
        title.add_css_class("eden-title")
        title.set_xalign(0)
        content.append(title)
        message = (
            "Progress is turned off. Nothing is being recorded. "
            "Ask an adult if you would like them to turn it on."
        )
        self._append_empty(content, message)

    def _render_help(self, content: Gtk.Box) -> None:
        title = Gtk.Label(label="Ask an adult for help")
        title.add_css_class("eden-title")
        title.set_xalign(0)
        content.append(title)
        self._append_empty(content, "Please find an adult and ask them to help you.")
        self._append_empty(content, build_label())
        content.append(
            self._text_button("Return to the sign-in screen", self._return_to_login)
        )

    def _render_settings(self, content: Gtk.Box) -> None:
        title = Gtk.Label(label="Make Eden easier for you")
        title.add_css_class("eden-title")
        title.set_xalign(0)
        content.append(title)

        text_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        text_row.append(Gtk.Label(label="Text size"))
        text_row.append(self._text_button("Smaller text", self._smaller_text))
        text_row.append(self._text_button("Bigger text", self._bigger_text))
        text_row.append(Gtk.Label(label=f"{int(self.preferences.text_scale * 100)}%"))
        content.append(text_row)

        contrast_label = "On" if self.preferences.high_contrast else "Off"
        content.append(
            self._text_button(
                f"High contrast: {contrast_label}", self._toggle_high_contrast
            )
        )
        motion_label = "On" if self.preferences.reduced_motion else "Off"
        content.append(
            self._text_button(
                f"Reduce motion: {motion_label}", self._toggle_reduced_motion
            )
        )
        content.append(Gtk.Label(label="Quick choices"))
        content.append(self._text_button("Calm default", self._use_calm_preset))
        content.append(self._text_button("Clear and large", self._use_clear_large_preset))
        content.append(self._text_button("High contrast", self._use_high_contrast_preset))
        content.append(self._text_button("Reset accessibility", self._use_calm_preset))
        saved_note = Gtk.Label(label="These choices are saved on this computer only.")
        saved_note.add_css_class("eden-status")
        content.append(saved_note)
        motion_note = Gtk.Label(label="This first prototype uses no automatic animations.")
        motion_note.add_css_class("eden-status")
        content.append(motion_note)

    def _append_empty(self, content: Gtk.Box, message: str) -> None:
        label = Gtk.Label(label=message)
        label.add_css_class("eden-empty")
        label.set_wrap(True)
        label.set_xalign(0)
        content.append(label)

    def _show_status(self, message: str) -> None:
        if getattr(self, "_status_label", None) is not None:
            self._status_label.set_label(message)
            return
        self._status_label = Gtk.Label(label=message)
        self._status_label.add_css_class("eden-status")
        self._status_label.set_wrap(True)
        self._status_label.set_xalign(0)
        child = getattr(self, "_root_container", None)
        if child is None:
            child = self.get_child()
        if isinstance(child, Gtk.Box):
            child.append(self._status_label)

    def _update(self, focus_page: bool = False) -> None:
        self._render()
        if focus_page and self._page_focus_target is not None:
            self._page_focus_target.grab_focus()

    def _go_home(self, _button: Gtk.Button) -> None:
        self.state.go_home()
        self._update(focus_page=True)

    def _open_category(self, category: str):
        def open_page(_button: Gtk.Button) -> None:
            self.state.open_category(category)
            self._update(focus_page=True)

        return open_page

    def _open_progress(self, _button: Gtk.Button) -> None:
        self.state.open_progress()
        self._update(focus_page=True)

    def _open_help(self, _button: Gtk.Button) -> None:
        self.state.open_help()
        self._update(focus_page=True)

    def _open_kidstube(self, _button: Gtk.Button) -> None:
        if not browser_access_ready():
            self._show_status(
                "KidsTube is unavailable until its adult-approved browser settings are ready."
            )
            return
        try:
            Gio.Subprocess.new(
                ["/usr/local/bin/eden-kidstube"], Gio.SubprocessFlags.NONE
            )
        except GLib.Error:  # pragma: no cover - actual browser launch needs Debian image
            self._show_status("KidsTube isn't available right now. Ask an adult for help.")

    def _open_settings(self, _button: Gtk.Button) -> None:
        self.state.open_settings()
        self._update(focus_page=True)

    def _return_to_login(self, _button: Gtk.Button) -> None:
        # The child session ends; LightDM then presents its normal authenticated
        # sign-in screen. No adult credentials are handled by Eden.
        self.get_application().quit()

    def _confirm_power_off(self, _button: Gtk.Button) -> None:
        dialog = Gtk.Window(application=self.get_application())
        dialog.connect("close-request", self._close_power_off_dialog)
        dialog.set_title("Turn off Eden OS")
        dialog.set_default_size(560, 360)
        dialog.set_modal(True)
        dialog.set_transient_for(self)
        dialog.set_resizable(False)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=22)
        box.set_margin_top(28)
        box.set_margin_bottom(28)
        box.set_margin_start(32)
        box.set_margin_end(32)
        dialog.set_child(box)

        heading = Gtk.Label(label="Ready to finish for now?")
        heading.add_css_class("eden-title")
        heading.set_xalign(0)
        box.append(heading)

        reminder = Gtk.Label(
            label="Close your activities and save your work before turning off the computer."
        )
        reminder.add_css_class("eden-status")
        reminder.set_wrap(True)
        reminder.set_xalign(0)
        box.append(reminder)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        keep_using = self._text_button("Keep using Eden", lambda _button: dialog.close())
        power_off = self._text_button(
            "Turn off computer", lambda _button: self._request_power_off(dialog)
        )
        actions.append(keep_using)
        actions.append(power_off)
        box.append(actions)
        dialog.present()

    def _close_power_off_dialog(self, _dialog: Gtk.Window) -> bool:
        return getattr(self, "_shutdown_pending", False)

    def _request_power_off(self, dialog: Gtk.Window) -> None:
        if getattr(self, "_shutdown_pending", False):
            return
        self._shutdown_pending = True
        dialog.set_sensitive(False)
        threading.Thread(target=self._power_off_worker, args=(dialog,), daemon=True).start()

    def _power_off_worker(self, dialog: Gtk.Window) -> None:
        failed = False
        try:
            connection = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            connection.call_sync(
                "org.freedesktop.login1",
                "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager",
                "PowerOff",
                GLib.Variant("(b)", (False,)),
                None,
                Gio.DBusCallFlags.NONE,
                30_000,
                None,
            )
        except GLib.Error:
            failed = True
        GLib.idle_add(self._finish_power_off, dialog, failed)

    def _finish_power_off(self, dialog: Gtk.Window, failed: bool) -> bool:
        self._shutdown_pending = False
        dialog.close()
        if failed:
            self._show_status(
                "Eden couldn't turn off the computer. Please ask an adult for help."
            )
        return False

    def _store_preferences(self, preferences: AccessibilityPreferences) -> None:
        try:
            save_preferences(preferences)
        except OSError:
            self._show_status(
                "Eden couldn't save these choices. Your current settings are unchanged. "
                "Please ask an adult for help."
            )
            return
        self.preferences = preferences
        self._apply_preferences()
        self._update()

    def _bigger_text(self, _button: Gtk.Button) -> None:
        next_scale = min(1.6, round(self.preferences.text_scale + 0.1, 1))
        self._store_preferences(
            AccessibilityPreferences(
                next_scale,
                self.preferences.high_contrast,
                self.preferences.reduced_motion,
            )
        )

    def _smaller_text(self, _button: Gtk.Button) -> None:
        next_scale = max(1.0, round(self.preferences.text_scale - 0.1, 1))
        self._store_preferences(
            AccessibilityPreferences(
                next_scale,
                self.preferences.high_contrast,
                self.preferences.reduced_motion,
            )
        )

    def _toggle_high_contrast(self, _button: Gtk.Button) -> None:
        self._store_preferences(
            AccessibilityPreferences(
                self.preferences.text_scale,
                not self.preferences.high_contrast,
                self.preferences.reduced_motion,
            )
        )

    def _toggle_reduced_motion(self, _button: Gtk.Button) -> None:
        self._store_preferences(
            AccessibilityPreferences(
                self.preferences.text_scale,
                self.preferences.high_contrast,
                not self.preferences.reduced_motion,
            )
        )

    def _use_calm_preset(self, _button: Gtk.Button) -> None:
        self._store_preferences(accessibility_preset("calm"))

    def _use_clear_large_preset(self, _button: Gtk.Button) -> None:
        self._store_preferences(accessibility_preset("clear-large"))

    def _use_high_contrast_preset(self, _button: Gtk.Button) -> None:
        self._store_preferences(accessibility_preset("high-contrast"))


class EdenApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id="uk.edenos.Home",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self) -> None:
        window = self.props.active_window or EdenWindow(self)
        window.present()


def main() -> int:
    return EdenApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())


