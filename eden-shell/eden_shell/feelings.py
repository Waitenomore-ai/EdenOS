"""Offline feelings check-in and quiet-space actions."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise SystemExit("Feelings and Quiet Space needs the Debian GTK 4 runtime.") from exc

from .feelings_model import CALM_ACTIONS, FEELINGS, FeelingsSpace


class FeelingsWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden Feelings and Quiet Space")
        self.set_default_size(760, 620)
        self.space = FeelingsSpace()
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        root.set_margin_top(30)
        root.set_margin_bottom(30)
        root.set_margin_start(38)
        root.set_margin_end(38)
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
        title = Gtk.Label(label="Feelings and Quiet Space")
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
            Path(__file__).parent / "data" / "activity-art" / "feelings-quiet-space.svg"
        ))
        illustration.set_pixel_size(150)
        illustration.set_halign(Gtk.Align.CENTER)
        root.append(illustration)
        intro = Gtk.Label(label="Choose a word for how you feel. There is no right answer.")
        intro.add_css_class("eden-subtitle")
        intro.set_wrap(True)
        intro.set_xalign(0)
        root.append(intro)
        moods = Gtk.FlowBox()
        moods.set_selection_mode(Gtk.SelectionMode.NONE)
        moods.set_homogeneous(True)
        moods.set_min_children_per_line(2)
        moods.set_max_children_per_line(4)
        root.append(moods)
        for feeling in FEELINGS:
            moods.insert(self._button(f"{feeling.symbol}  {feeling.label}", lambda _b, key=feeling.key: self._mood(key)), -1)
        self.actions = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.append(self.actions)
        for index, (symbol, label) in enumerate(CALM_ACTIONS):
            self.actions.append(self._button(f"{symbol}  {label}", lambda _b, i=index: self._action(i)))
        self.status = Gtk.Label()
        self.status.add_css_class("eden-status")
        self.status.add_css_class("eden-game-feedback")
        self.status.set_wrap(True)
        self.status.set_xalign(0)
        root.append(self.status)
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
        mood = self.space.mood.label if self.space.mood else "not chosen yet"
        self.status.set_label(f"Feeling: {mood}. Calm actions completed: {self.space.completed_count} of 3.")

    def _mood(self, key: str) -> None:
        self.space.choose_mood(key)
        self._refresh()

    def _action(self, index: int) -> None:
        self.space.toggle_action(index)
        self._refresh()

    def _reset(self, _button: Gtk.Button) -> None:
        self.space.reset()
        self._refresh()


class FeelingsApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="uk.edenos.Feelings", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or FeelingsWindow(self)
        window.present()


def main() -> int:
    return FeelingsApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
