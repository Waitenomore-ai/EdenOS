"""Accessible, offline first-letter matching game."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise SystemExit("Word Woodland needs the Debian GTK 4 runtime.") from exc

from .word_woodland_model import WordWoodland


class WordWoodlandWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden Word Woodland")
        self.set_default_size(760, 620)
        self.game = WordWoodland()

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

        title = Gtk.Label(label="Word Woodland")
        title.add_css_class("eden-game-heading")
        title.set_xalign(0)
        root.append(title)
        illustration = Gtk.Image.new_from_file(str(
            Path(__file__).parent / "data" / "activity-art" / "word-woodland.svg"
        ))
        illustration.set_pixel_size(150)
        illustration.set_halign(Gtk.Align.CENTER)
        root.append(illustration)
        self.prompt = Gtk.Label(label="Which letter starts this word?")
        self.prompt.add_css_class("eden-subtitle")
        self.prompt.set_xalign(0)
        root.append(self.prompt)
        self.picture = Gtk.Label()
        self.picture.add_css_class("eden-game-picture")
        self.picture.set_xalign(0)
        root.append(self.picture)
        self.word = Gtk.Label()
        self.word.add_css_class("eden-card-label")
        self.word.set_xalign(0)
        root.append(self.word)

        self.choices = Gtk.FlowBox()
        self.choices.set_selection_mode(Gtk.SelectionMode.NONE)
        self.choices.set_min_children_per_line(2)
        self.choices.set_max_children_per_line(2)
        self.choices.set_column_spacing(18)
        self.choices.set_row_spacing(18)
        self.choices.set_homogeneous(True)
        root.append(self.choices)
        self.feedback = Gtk.Label(label="Choose a letter when you are ready.")
        self.feedback.add_css_class("eden-game-feedback")
        self.feedback.set_wrap(True)
        self.feedback.set_xalign(0)
        root.append(self.feedback)
        root.append(self._button("New word", self._new_round))
        self._new_round()

    def _button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("eden-game-button")
        button.set_size_request(90, 64)
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.connect("clicked", callback)
        return button

    def _new_round(self, _button: Gtk.Button | None = None) -> None:
        current = self.game.new_round()
        self.picture.set_label(current.symbol)
        self.picture.update_property([Gtk.AccessibleProperty.LABEL], [f"Picture for {current.word}"])
        self.word.set_label(current.word)
        while child := self.choices.get_first_child():
            self.choices.remove(child)
        for value in current.choices:
            self.choices.insert(self._button(value, lambda _button, v=value: self._answer(v)), -1)
        self.feedback.set_label("Choose a letter when you are ready.")

    def _answer(self, value: str) -> None:
        if self.game.answer(value):
            self.feedback.set_label("That is right! You found the first letter.")
        else:
            self.feedback.set_label("Not quite. Say the word slowly and try again.")


class WordWoodlandApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="uk.edenos.WordWoodland", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or WordWoodlandWindow(self)
        window.present()


def main() -> int:
    return WordWoodlandApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
