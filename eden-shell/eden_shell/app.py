"""GTK 4 child-facing Eden OS launcher."""

from __future__ import annotations

import sys
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
from .preferences import (
    AccessibilityPreferences,
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
        self.preferences = load_preferences()
        self._install_styles()
        self._apply_preferences()
        self._render()

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

    def _accessible_button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button()
        button.update_property_value([Gtk.AccessibleProperty.LABEL], [label])
        button.add_css_class("eden-small-button")
        button.connect("clicked", callback)
        return button

    def _text_button(self, label: str, callback) -> Gtk.Button:
        button = self._accessible_button(label, callback)
        button.set_label(label)
        return button

    def _tile(self, label: str, icon_name: str, callback) -> Gtk.Button:
        button = Gtk.Button()
        button.update_property_value([Gtk.AccessibleProperty.LABEL], [label])
        button.add_css_class("eden-card")
        button.connect("clicked", callback)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        content.set_halign(Gtk.Align.CENTER)
        icon_path = Path(__file__).parent / "data" / "icons" / f"{icon_name}.svg"
        image = Gtk.Image.new_from_file(str(icon_path))
        image.set_pixel_size(48)
        image.set_focusable(False)
        content.append(image)
        title = Gtk.Label(label=label)
        title.add_css_class("eden-card-label")
        content.append(title)
        button.set_child(content)
        return button

    def _render(self) -> None:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(22)
        root.set_margin_bottom(22)
        root.set_margin_start(28)
        root.set_margin_end(28)
        self.set_child(root)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        if self.state.page != "home":
            header.append(self._text_button("Home", self._go_home))
        logo_path = Path("/usr/share/pixmaps/edenos-logo.png")
        if logo_path.is_file():
            logo = Gtk.Image.new_from_file(str(logo_path))
            logo.set_pixel_size(88)
            logo.set_tooltip_text("Eden OS")
            header.append(logo)
        heading = Gtk.Label(label="Eden OS")
        heading.add_css_class("eden-title")
        heading.set_hexpand(True)
        heading.set_xalign(0)
        header.append(heading)
        header.append(self._text_button("Accessibility settings", self._open_settings))
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
        welcome = Gtk.Label(label="Hello, explorer!")
        welcome.add_css_class("eden-title")
        welcome.set_xalign(0)
        content.append(welcome)
        prompt = Gtk.Label(label="What would you like to do today?")
        prompt.add_css_class("eden-subtitle")
        prompt.set_xalign(0)
        content.append(prompt)

        grid = Gtk.FlowBox()
        grid.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.set_min_children_per_line(1)
        grid.set_max_children_per_line(2)
        grid.set_column_spacing(18)
        grid.set_row_spacing(18)
        grid.set_homogeneous(True)
        grid.set_hexpand(True)
        for category in CATEGORIES:
            grid.insert(self._tile(category.label, category.icon, self._open_category(category.slug)), -1)
        content.append(grid)

        footer = Gtk.FlowBox()
        footer.set_selection_mode(Gtk.SelectionMode.NONE)
        footer.set_min_children_per_line(1)
        footer.set_max_children_per_line(2)
        footer.set_column_spacing(16)
        footer.set_row_spacing(16)
        footer.insert(self._text_button("My Progress", self._open_progress), -1)
        browser_button = self._text_button("Watch KidsTube online", self._open_kidstube)
        browser_button.set_sensitive(browser_access_ready())
        footer.insert(browser_button, -1)
        footer.insert(self._text_button("Ask an adult for help", self._open_help), -1)
        footer.insert(self._text_button("Turn off computer", self._confirm_power_off), -1)
        content.append(footer)
        self._append_empty(content, "Your included activities work offline. Online video needs an internet connection and adult setup.")

    def _render_category(self, content: Gtk.Box) -> None:
        category = next(item for item in CATEGORIES if item.slug == self.state.category)
        title = Gtk.Label(label=category.label)
        title.add_css_class("eden-title")
        title.set_xalign(0)
        content.append(title)
        activities = [item for item in self.catalogue if item.category == category.slug]
        if not activities:
            self._append_empty(content, "Your adult can add activities here.")
            return
        for activity in activities:
            self._append_activity(content, activity)

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
        app_info = Gio.DesktopAppInfo.new(activity.desktop_id)
        if app_info is None:
            self._show_status("I couldn't open that activity. Ask an adult for help.")
            return
        try:
            app_info.launch([], None)
        except GLib.Error:  # pragma: no cover - actual desktop launch requires GTK session
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
        self._status_label = Gtk.Label(label=message)
        self._status_label.add_css_class("eden-status")
        self._status_label.set_wrap(True)
        self._status_label.set_xalign(0)
        child = self.get_child()
        if isinstance(child, Gtk.Box):
            child.append(self._status_label)

    def _update(self) -> None:
        self._render()

    def _go_home(self, _button: Gtk.Button) -> None:
        self.state.go_home()
        self._update()

    def _open_category(self, category: str):
        def open_page(_button: Gtk.Button) -> None:
            self.state.open_category(category)
            self._update()

        return open_page

    def _open_progress(self, _button: Gtk.Button) -> None:
        self.state.open_progress()
        self._update()

    def _open_help(self, _button: Gtk.Button) -> None:
        self.state.open_help()
        self._update()

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
        self._update()

    def _return_to_login(self, _button: Gtk.Button) -> None:
        # The child session ends; LightDM then presents its normal authenticated
        # sign-in screen. No adult credentials are handled by Eden.
        self.get_application().quit()

    def _confirm_power_off(self, _button: Gtk.Button) -> None:
        dialog = Gtk.Window(application=self.get_application())
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

    def _request_power_off(self, dialog: Gtk.Window) -> None:
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
            dialog.close()
            self._show_status(
                "Eden couldn't turn off the computer. Please ask an adult for help."
            )

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

