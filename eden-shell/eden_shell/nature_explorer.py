"""Offline nature observation cards with a calm, keyboard-friendly GTK interface."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise SystemExit("Nature Explorer needs the Debian GTK 4 runtime.") from exc

from .nature_explorer_model import NatureExplorer


class NatureExplorerWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden Nature Explorer")
        self.set_default_size(760, 620)
        self.explorer = NatureExplorer()

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=22)
        root.set_margin_top(34)
        root.set_margin_bottom(34)
        root.set_margin_start(40)
        root.set_margin_end(40)
        provider = Gtk.CssProvider()
        provider.load_from_path(str(Path(__file__).parent / "data" / "eden.css"))
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self._style_provider = provider
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(root)
        self.set_child(scroll)
        root.add_css_class("eden-game-panel")

        title = Gtk.Label(label="Nature Explorer")
        title.add_css_class("eden-game-heading")
        title.set_xalign(0)
        root.append(title)
        back_home = Gtk.Button(label="← Back to Eden Home")
        back_home.add_css_class("eden-game-back")
        back_home.set_halign(Gtk.Align.START)
        back_home.set_size_request(200, 62)
        back_home.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Close game and return to Eden Home"]
        )
        back_home.connect("clicked", lambda _button: self.close())
        root.append(back_home)
        illustration = Gtk.Image.new_from_file(str(
            Path(__file__).parent / "data" / "activity-art" / "nature-explorer.svg"
        ))
        illustration.set_pixel_size(150)
        illustration.set_halign(Gtk.Align.CENTER)
        root.append(illustration)
        self.card = Gtk.Label()
        self.card.add_css_class("eden-game-picture")
        self.card.set_wrap(True)
        self.card.set_xalign(0.5)
        root.append(self.card)
        self.hint = Gtk.Label()
        self.hint.add_css_class("eden-subtitle")
        self.hint.set_wrap(True)
        self.hint.set_xalign(0.5)
        root.append(self.hint)
        self.status = Gtk.Label()
        self.status.add_css_class("eden-status")
        self.status.add_css_class("eden-game-feedback")
        self.status.set_wrap(True)
        self.status.set_xalign(0.5)
        root.append(self.status)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        controls.set_homogeneous(True)
        controls.set_halign(Gtk.Align.FILL)
        root.append(controls)
        controls.append(self._button("Previous", self._previous))
        controls.append(self._button("I found it", self._found))
        controls.append(self._button("Next", self._next))
        root.append(self._button("Start again", self._reset))
        self._refresh()

    def _button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("eden-game-button")
        button.set_size_request(90, 64)
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.connect("clicked", callback)
        return button

    def _refresh(self) -> None:
        item = self.explorer.current
        self.card.set_label(f"{item.symbol}  {item.label}")
        self.card.update_property([Gtk.AccessibleProperty.LABEL], [item.label])
        self.hint.set_label(item.hint)
        found = "Found today" if self.explorer.is_found else "Not marked yet"
        self.status.set_label(f"{found}. {self.explorer.found_count} of 6 found.")

    def _previous(self, _button: Gtk.Button) -> None:
        self.explorer.previous()
        self._refresh()

    def _next(self, _button: Gtk.Button) -> None:
        self.explorer.next()
        self._refresh()

    def _found(self, _button: Gtk.Button) -> None:
        self.explorer.mark_found()
        self._refresh()

    def _reset(self, _button: Gtk.Button) -> None:
        self.explorer.reset()
        self._refresh()


class NatureExplorerApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="uk.edenos.NatureExplorer", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or NatureExplorerWindow(self)
        window.present()


def main() -> int:
    return NatureExplorerApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
