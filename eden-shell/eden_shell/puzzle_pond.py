"""Accessible, offline matching-pairs activity."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, GLib, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise SystemExit("Puzzle Pond needs the Debian GTK 4 runtime.") from exc

from .puzzle_pond_model import PuzzlePond


class PuzzlePondWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden Puzzle Pond")
        self.set_default_size(820, 680)
        self.game = PuzzlePond()
        self._mismatch_timeout_id = None

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
        title = Gtk.Label(label="Puzzle Pond")
        title.add_css_class("eden-game-heading")
        title.set_xalign(0)
        root.append(title)
        prompt = Gtk.Label(label="Find the two matching pond friends. There is no timer.")
        prompt.add_css_class("eden-subtitle")
        prompt.set_xalign(0)
        prompt.set_wrap(True)
        root.append(prompt)
        self.cards = Gtk.Grid()
        self.cards.set_row_spacing(14)
        self.cards.set_column_spacing(14)
        self.cards.set_halign(Gtk.Align.CENTER)
        root.append(self.cards)
        self.status = Gtk.Label(label="Choose a card when you are ready.")
        self.status.add_css_class("eden-status")
        self.status.set_xalign(0)
        self.status.add_css_class("eden-game-feedback")
        self.status.set_wrap(True)
        root.append(self.status)
        root.append(self._button("Start again", self._restart))
        self._render()

    def _button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("eden-game-button")
        button.set_size_request(90, 64)
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.connect("clicked", callback)
        return button

    def _render(self) -> None:
        while child := self.cards.get_first_child():
            self.cards.remove(child)
        for card in self.game.cards:
            label = card.symbol if card.revealed or card.matched else "?"
            button = self._button(label, lambda _button, i=card.index: self._choose(i))
            button.set_size_request(125, 110)
            button.set_sensitive(not card.matched and not card.revealed)
            button.update_property([Gtk.AccessibleProperty.LABEL], [
                f"Card {card.index + 1}: {card.symbol if card.revealed or card.matched else 'hidden'}"
            ])
            self.cards.attach(button, card.index % 4, card.index // 4, 1, 1)

    def _choose(self, index: int) -> None:
        if self._mismatch_timeout_id is not None:
            return
        result = self.game.choose(index)
        if result == "matched":
            self.status.set_label("A match! Find another pair.")
        elif result == "second":
            if self.game.first is not None and self.game.second is not None:
                first = self.game.cards[self.game.first]
                second = self.game.cards[self.game.second]
                if first.symbol != second.symbol:
                    self.status.set_label("Those are different. Try another pair.")
                    self._render()
                    self._mismatch_timeout_id = GLib.timeout_add(1100, self._finish_mismatch)
                    return
                else:
                    self.status.set_label("A match! Find another pair.")
        if self.game.complete:
            self.status.set_label("The pond is complete! Start again whenever you like.")
        self._render()

    def _finish_mismatch(self) -> bool:
        self._mismatch_timeout_id = None
        self.game.finish_mismatch()
        self._render()
        return GLib.SOURCE_REMOVE

    def _restart(self, _button: Gtk.Button) -> None:
        if self._mismatch_timeout_id is not None:
            GLib.source_remove(self._mismatch_timeout_id)
            self._mismatch_timeout_id = None
        self.game.restart()
        self.status.set_label("Choose a card when you are ready.")
        self._render()


class PuzzlePondApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="uk.edenos.PuzzlePond", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or PuzzlePondWindow(self)
        window.present()


def main() -> int:
    return PuzzlePondApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
