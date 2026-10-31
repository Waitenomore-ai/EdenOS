"""Offline counting game with a calm, keyboard-friendly GTK interface."""

from __future__ import annotations

import sys

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise SystemExit("Number Meadow needs the Debian GTK 4 runtime.") from exc

from .number_meadow_model import NumberMeadow


class NumberMeadowWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden Number Meadow")
        self.set_default_size(760, 620)
        self.set_resizable(True)
        self.game = NumberMeadow()

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=22)
        root.set_margin_top(34)
        root.set_margin_bottom(34)
        root.set_margin_start(40)
        root.set_margin_end(40)
        self.set_child(root)

        title = Gtk.Label(label="Number Meadow")
        title.add_css_class("eden-title")
        title.set_xalign(0)
        root.append(title)
        self.prompt = Gtk.Label()
        self.prompt.add_css_class("eden-subtitle")
        self.prompt.set_wrap(True)
        self.prompt.set_xalign(0)
        root.append(self.prompt)

        self.choices = Gtk.FlowBox()
        self.choices.set_selection_mode(Gtk.SelectionMode.NONE)
        self.choices.set_min_children_per_line(2)
        self.choices.set_max_children_per_line(2)
        self.choices.set_column_spacing(18)
        self.choices.set_row_spacing(18)
        self.choices.set_homogeneous(True)
        root.append(self.choices)

        self.feedback = Gtk.Label(label="Choose an answer when you are ready.")
        self.feedback.set_wrap(True)
        self.feedback.set_xalign(0)
        root.append(self.feedback)
        root.append(self._button("New meadow", self._new_round))
        self._new_round()

    def _button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("eden-small-button")
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.connect("clicked", callback)
        return button

    def _new_round(self, _button: Gtk.Button | None = None) -> None:
        current = self.game.new_round()
        self.prompt.set_label(f"How many flowers are in the meadow?  {current.count} flowers are shown.")
        while child := self.choices.get_first_child():
            self.choices.remove(child)
        for value in current.choices:
            self.choices.insert(self._button(str(value), lambda _button, v=value: self._answer(v)), -1)
        self.feedback.set_label("Choose an answer when you are ready.")

    def _answer(self, value: int) -> None:
        if self.game.answer(value):
            self.feedback.set_label("That is right! Great counting. Try another meadow when you are ready.")
        else:
            self.feedback.set_label("Not quite. Have another look and try again.")


class NumberMeadowApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="uk.edenos.NumberMeadow", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or NumberMeadowWindow(self)
        window.present()


def main() -> int:
    return NumberMeadowApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
