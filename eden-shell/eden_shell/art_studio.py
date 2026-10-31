"""Offline sticker-board art activity with large accessible controls."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise SystemExit("Art Studio needs the Debian GTK 4 runtime.") from exc

from .art_studio_model import ArtBoard


class ArtStudioWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden Art Studio")
        self.set_default_size(820, 680)
        self.board = ArtBoard()
        self.colour = "sunny yellow"

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        root.set_margin_top(30)
        root.set_margin_bottom(30)
        root.set_margin_start(36)
        root.set_margin_end(36)
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
        title = Gtk.Label(label="Art Studio")
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
            Path(__file__).parent / "data" / "activity-art" / "art-studio.svg"
        ))
        illustration.set_pixel_size(150)
        illustration.set_halign(Gtk.Align.CENTER)
        root.append(illustration)
        prompt = Gtk.Label(label="Choose a sticker, then add it to your picture.")
        prompt.add_css_class("eden-subtitle")
        prompt.set_xalign(0)
        prompt.set_wrap(True)
        root.append(prompt)

        tools = Gtk.FlowBox()
        tools.set_selection_mode(Gtk.SelectionMode.NONE)
        tools.set_min_children_per_line(2)
        tools.set_max_children_per_line(4)
        tools.set_column_spacing(12)
        tools.set_row_spacing(12)
        for symbol in ("🌼", "🌈", "🦋", "⭐", "🌳", "💧"):
            tools.insert(self._button(symbol, lambda _button, s=symbol: self._add(s)), -1)
        root.append(tools)

        self.canvas = Gtk.FlowBox()
        self.canvas.set_selection_mode(Gtk.SelectionMode.NONE)
        self.canvas.set_min_children_per_line(4)
        self.canvas.set_max_children_per_line(8)
        self.canvas.set_column_spacing(10)
        self.canvas.set_row_spacing(10)
        self.canvas.set_vexpand(True)
        root.append(self.canvas)
        self.status = Gtk.Label(label="Your picture is empty. Add a sticker to begin.")
        self.status.add_css_class("eden-status")
        self.status.set_xalign(0)
        self.status.add_css_class("eden-game-feedback")
        self.status.set_wrap(True)
        root.append(self.status)
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        actions.append(self._button("Undo", self._undo))
        actions.append(self._button("Clear picture", self._clear))
        root.append(actions)

    def _button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("eden-game-button")
        button.set_size_request(90, 64)
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.connect("clicked", callback)
        return button

    def _add(self, symbol: str) -> None:
        if not self.board.add(symbol, self.colour):
            self.status.set_label("This picture is full. Clear it or undo a sticker to keep creating.")
            return
        self._render()

    def _render(self) -> None:
        while child := self.canvas.get_first_child():
            self.canvas.remove(child)
        for stamp in self.board.stamps:
            sticker = Gtk.Label(label=stamp.symbol)
            sticker.add_css_class("eden-card-label")
            sticker.set_size_request(65, 65)
            self.canvas.insert(sticker, -1)
        count = len(self.board.stamps)
        self.status.set_label(f"Your picture has {count} sticker{'s' if count != 1 else ''}.")

    def _undo(self, _button: Gtk.Button) -> None:
        self.board.undo()
        self._render()

    def _clear(self, _button: Gtk.Button) -> None:
        self.board.clear()
        self._render()


class ArtStudioApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="uk.edenos.ArtStudio", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or ArtStudioWindow(self)
        window.present()


def main() -> int:
    return ArtStudioApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
