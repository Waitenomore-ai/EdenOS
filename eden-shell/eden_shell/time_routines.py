"""Predictable offline routine checklist with accessible controls."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise SystemExit("Time and Routines needs the Debian GTK 4 runtime.") from exc

from .time_routines_model import Routine, STEPS


class TimeRoutinesWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden Time and Routines")
        self.set_default_size(820, 680)
        self.routine = Routine()

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
        title = Gtk.Label(label="Time and Routines")
        title.add_css_class("eden-game-heading")
        title.set_xalign(0)
        root.append(title)
        illustration = Gtk.Image.new_from_file(str(
            Path(__file__).parent / "data" / "activity-art" / "time-routines.svg"
        ))
        illustration.set_pixel_size(150)
        illustration.set_halign(Gtk.Align.CENTER)
        root.append(illustration)
        prompt = Gtk.Label(label="Take one step at a time. You can change your choices.")
        prompt.add_css_class("eden-subtitle")
        prompt.set_xalign(0)
        prompt.set_wrap(True)
        root.append(prompt)
        self.steps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.append(self.steps_box)
        self.status = Gtk.Label(label="Nothing is checked yet.")
        self.status.add_css_class("eden-status")
        self.status.set_xalign(0)
        self.status.add_css_class("eden-game-feedback")
        self.status.set_wrap(True)
        root.append(self.status)
        root.append(self._button("Start again", self._reset))
        self._render()

    def _button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("eden-game-button")
        button.set_size_request(90, 64)
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.connect("clicked", callback)
        return button

    def _render(self) -> None:
        while child := self.steps_box.get_first_child():
            self.steps_box.remove(child)
        for index, step in enumerate(STEPS):
            mark = "✓" if self.routine.completed[index] else "○"
            label = f"{mark}  {step.symbol}  {step.label}"
            self.steps_box.append(self._button(label, lambda _button, i=index: self._toggle(i)))
        count = sum(self.routine.completed)
        self.status.set_label(
            "Routine complete. Well done!" if self.routine.finished
            else f"{count} of {len(STEPS)} steps complete."
        )

    def _toggle(self, index: int) -> None:
        self.routine.toggle(index)
        self._render()

    def _reset(self, _button: Gtk.Button) -> None:
        self.routine.reset()
        self._render()


class TimeRoutinesApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="uk.edenos.TimeRoutines", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or TimeRoutinesWindow(self)
        window.present()


def main() -> int:
    return TimeRoutinesApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
