"""Accessible offline picture-story activity."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, Gtk
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise SystemExit("Story Garden needs the Debian GTK 4 runtime.") from exc

from .story_garden_model import StoryGarden


class StoryGardenWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Eden Story Garden")
        self.set_default_size(760, 620)
        self.story = StoryGarden()

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

        title = Gtk.Label(label="Story Garden")
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
            Path(__file__).parent / "data" / "activity-art" / "story-garden.svg"
        ))
        illustration.set_pixel_size(150)
        illustration.set_halign(Gtk.Align.CENTER)
        root.append(illustration)
        prompt = Gtk.Label(label="Read the story one picture at a time.")
        prompt.add_css_class("eden-subtitle")
        prompt.set_xalign(0)
        prompt.set_wrap(True)
        root.append(prompt)
        self.picture = Gtk.Label()
        self.picture.add_css_class("eden-game-picture")
        self.picture.set_xalign(0)
        root.append(self.picture)
        self.sentence = Gtk.Label()
        self.sentence.add_css_class("eden-card-label")
        self.sentence.set_xalign(0)
        self.sentence.set_wrap(True)
        root.append(self.sentence)
        self.progress = Gtk.Label()
        self.progress.add_css_class("eden-status")
        self.progress.set_xalign(0)
        root.append(self.progress)
        self.next_button = self._button("Next scene", self._next)
        root.append(self.next_button)
        root.append(self._button("Start again", self._restart))
        self._render_scene()

    def _button(self, label: str, callback) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("eden-game-button")
        button.set_size_request(90, 64)
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.connect("clicked", callback)
        return button

    def _render_scene(self) -> None:
        scene = self.story.scene
        self.picture.set_label(scene.symbol)
        self.picture.update_property([Gtk.AccessibleProperty.LABEL], ["Story picture"])
        self.sentence.set_label(scene.sentence)
        self.progress.set_label(f"Scene {self.story.position + 1} of 4")
        self.next_button.set_label("Finish story" if self.story.finished else "Next scene")
        self.next_button.set_sensitive(not self.story.finished)

    def _next(self, _button: Gtk.Button) -> None:
        self.story.next_scene()
        self._render_scene()

    def _restart(self, _button: Gtk.Button) -> None:
        self.story.restart()
        self._render_scene()


class StoryGardenApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="uk.edenos.StoryGarden", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or StoryGardenWindow(self)
        window.present()


def main() -> int:
    return StoryGardenApplication().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
