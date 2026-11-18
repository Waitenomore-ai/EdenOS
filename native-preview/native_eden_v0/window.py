"""Eden native desktop prototype with opt-in, read-only child cards."""
from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)
from .eden_core.profile_cards import APPROVED_AVATARS, make_profile_card
from .eden_core.profile_source import read_profile_cards
from .eden_core.profile_chooser_model import ProfileChooser
from .eden_core.parent_pin import has_pin, verify_pin
from .eden_core.activity_visibility import REVIEWED_RATINGS
from .eden_core.garden_stars import CATALOGUE, ACTIVITIES

class EdenNativeWindow(QMainWindow):
    def __init__(self, profile_source: Path | None = None):
        super().__init__()
        self.setWindowTitle("Eden's Garden — Native Desktop Preview")
        self.resize(1000, 690)
        self._is_demo = profile_source is None
        if self._is_demo:
            cards = [
                make_profile_card("demo_" + avatar.removeprefix("approved-"),
                                  avatar.removeprefix("approved-").title(), avatar)
                for avatar in APPROVED_AVATARS
            ]
        else:
            cards = read_profile_cards(Path(profile_source))
        self._chooser = ProfileChooser(cards)
        self._unlocked = False
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._home = QWidget()
        layout = QVBoxLayout(self._home)
        layout.setContentsMargins(35, 26, 35, 26)
        title = QLabel("Welcome to Eden's Garden")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("heading")
        layout.addWidget(title)
        hint = QLabel(
            "Choose your picture to open your Eden space"
            if not self._is_demo else
            "Choose a character to explore — demonstration profiles only"
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        grid = QGridLayout()
        for index, card in enumerate(self._chooser.tiles()):
            name = card["display_name"]
            button = QPushButton(name)
            button.setAccessibleName(("Choose character " if self._is_demo else "Choose child ") + name)
            portrait_path = Path(__file__).parent / "assets" / "avatars" / (card["avatar"] + ".png")
            if portrait_path.is_file():
                button.setIcon(QIcon(str(portrait_path)))
                button.setIconSize(QSize(90, 116))
            button.setProperty("avatar_id", card["avatar"])
            button.setMinimumHeight(146)
            button.clicked.connect(lambda checked=False, i=index: self.choose_character(i))
            grid.addWidget(button, index // 4, index % 4)
        layout.addLayout(grid)
        self._selected_label = QLabel("Choose your character" if self._is_demo else "Choose your picture")
        self._selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._selected_label)
        parents = QPushButton("Parent Corner")
        parents.setAccessibleName("Open Parent Corner")
        parents.setMinimumHeight(54)
        parents.clicked.connect(self._show_parent)
        layout.addWidget(parents)
        self._stack.addWidget(self._home)
        self._child_home = QWidget()
        child_layout = QVBoxLayout(self._child_home)
        child_layout.setContentsMargins(35, 26, 35, 26)
        self._child_heading = QLabel("Welcome")
        self._child_heading.setObjectName("heading")
        self._child_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        child_layout.addWidget(self._child_heading)
        actions = QHBoxLayout()
        self._home_action_names = ("Play", "Learn", "Create")
        for action in self._home_action_names:
            button = QPushButton(action)
            button.setAccessibleName(action + " activities")
            image = Path(__file__).parent / "assets" / "home" / (action.lower() + ".png")
            if image.is_file():
                button.setIcon(QIcon(str(image)))
                button.setIconSize(QSize(260, 160))
            button.setMinimumSize(260, 180)
            button.clicked.connect(lambda checked=False, name=action: self.navigate_home_action(name))
            actions.addWidget(button)
        child_layout.addLayout(actions)
        self._child_feedback = QLabel("Activities are being connected to the approved iMac versions.")
        self._child_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._child_feedback.setWordWrap(True)
        child_layout.addWidget(self._child_feedback)
        child_layout.addStretch()
        footer = QHBoxLayout()
        profile_button = QPushButton("My Profile")
        profile_button.clicked.connect(lambda: self._child_feedback.setText("Profile settings are not yet connected."))
        footer.addWidget(profile_button)
        parent_button = QPushButton("Parent")
        parent_button.clicked.connect(self._show_parent)
        footer.addWidget(parent_button)
        logout_button = QPushButton("Log out")
        logout_button.clicked.connect(self.logout)
        footer.addWidget(logout_button)
        child_layout.addLayout(footer)
        self._stack.addWidget(self._child_home)
        self._parent = QWidget()
        parent_layout = QVBoxLayout(self._parent)
        parent_layout.setContentsMargins(60, 50, 60, 50)
        parent_title = QLabel("Parent Corner")
        parent_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_title.setObjectName("heading")
        parent_layout.addWidget(parent_title)
        self._parent_message = QLabel("Enter your existing Eden parent PIN to unlock.")
        self._parent_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(self._parent_message)
        self._pin = QLineEdit()
        self._pin.setAccessibleName("Parent PIN")
        self._pin.setEchoMode(QLineEdit.EchoMode.Password)
        self._pin.setPlaceholderText("Parent PIN")
        self._pin.setMaxLength(8)
        self._pin.returnPressed.connect(self._unlock_from_entry)
        parent_layout.addWidget(self._pin)
        unlock = QPushButton("Unlock Parent Corner")
        unlock.setAccessibleName("Unlock Parent Corner with PIN")
        unlock.clicked.connect(self._unlock_from_entry)
        parent_layout.addWidget(unlock)
        back = QPushButton("Home")
        back.clicked.connect(self.return_home)
        parent_layout.addWidget(back)
        parent_layout.addStretch()
        self._stack.addWidget(self._parent)
        self._parent_section_names = ("Child Profiles", "Activity Controls", "Learning Progress", "Garden Stars", "PIN & Security")
        self._dashboard = QWidget()
        dashboard_layout = QVBoxLayout(self._dashboard)
        dashboard_heading = QLabel("Parent Corner — Management")
        dashboard_heading.setObjectName("heading")
        dashboard_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashboard_layout.addWidget(dashboard_heading)
        self._parent_child_label = QLabel("No child selected")
        self._parent_child_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashboard_layout.addWidget(self._parent_child_label)
        sections = QGridLayout()
        for index, name in enumerate(self._parent_section_names):
            button = QPushButton(name.replace("&", "&&"))
            button.setMinimumHeight(76)
            button.clicked.connect(lambda checked=False, key=name: self._switch_parent_section(key))
            sections.addWidget(button, index // 3, index % 3)
        dashboard_layout.addLayout(sections)
        self._section_description = QLabel("Select a section. Controls are read-only in this prototype.")
        self._section_description.setWordWrap(True)
        self._section_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashboard_layout.addWidget(self._section_description)
        lock_button = QPushButton("Lock Parent Corner and Return Home")
        lock_button.setAccessibleName("Lock Parent Corner and return Home")
        lock_button.clicked.connect(self.return_home)
        dashboard_layout.addWidget(lock_button)
        dashboard_layout.addStretch()
        self._stack.addWidget(self._dashboard)
        self.setStyleSheet("""
            QWidget { background: #e9f5e8; color: #214b39; font-size: 21px; }
            QLabel#heading { font-size: 34px; font-weight: 700; padding: 12px; }
            QPushButton { background: #fff9e6; border: 2px solid #83b397;
                border-radius: 18px; padding: 12px; }
            QPushButton:focus { border: 3px solid #3a7452; }
            QLineEdit { background: white; padding: 12px; border-radius: 12px; }
        """)

    def current_page(self):
        pages = {
            self._home: "login",
            self._child_home: "home",
            self._parent: "parent-pin",
            self._dashboard: "parent-corner",
        }
        return pages.get(self._stack.currentWidget(), "unknown")

    def home_actions(self):
        return self._home_action_names

    def navigate_home_action(self, name):
        if self.current_page() != "home" or name not in self._home_action_names:
            return False
        self._child_feedback.setText(name + " will open when the approved activities are integrated.")
        return False

    def logout(self):
        self._chooser.select(-1)
        self._selected_label.setText("Choose your character" if self._is_demo else "Choose your picture")
        self._child_heading.setText("Welcome")
        self._child_feedback.setText("Activities are being connected to the approved iMac versions.")
        self._unlocked = False
        self._pin.clear()
        self._stack.setCurrentWidget(self._home)

    def character_count(self):
        return len(self._chooser.tiles())

    def character_names(self):
        return [item["display_name"] for item in self._chooser.tiles()]

    def choose_character(self, index):
        identifier = self._chooser.select(index)
        if identifier:
            card = self._chooser.selected_public_card()
            self._selected_label.setText("Selected: " + card["display_name"])
            self._child_heading.setText("Welcome, " + card["display_name"])
            self._stack.setCurrentWidget(self._child_home)
        return identifier

    def selected_profile_id(self):
        return self._chooser.selected_username()

    def parent_is_unlocked(self):
        return self._unlocked

    def parent_sections(self):
        return self._parent_section_names

    def parent_child_summary(self):
        return self._parent_child_label.text()

    def parent_section_description(self):
        return self._section_description.text()

    def _switch_parent_section(self, name):
        if not self._unlocked or name not in self._parent_section_names:
            return False
        if name == "Child Profiles":
            names = self.character_names()
            selected = self._chooser.selected_public_card()
            selected_name = selected["display_name"] if selected else "none"
            self._section_description.setText(
                f"{len(names)} {'demonstration profiles' if self._is_demo else 'child profiles'}: {', '.join(names)}. "
                f"Currently selected: {selected_name}. "
                + ("Read-only; no real child data loaded." if self._is_demo else "Read-only preview; no profiles modified.")
            )
        elif name == "Activity Controls":
            catalogue = ", ".join(sorted(REVIEWED_RATINGS))
            self._section_description.setText(
                f"{len(REVIEWED_RATINGS)} reviewed activities: {catalogue}. "
                "Read-only catalogue; no child-specific choices loaded."
            )
        elif name == "Learning Progress":
            self._section_description.setText(
                "Learning Progress — no learning records loaded. "
                "Demo profiles cannot display actual achievement or progress."
            )
        elif name == "Garden Stars":
            self._section_description.setText(
                f"Garden Stars: {len(CATALOGUE)} approved stickers and "
                f"{len(ACTIVITIES)} rewardable activities. "
                "Read-only catalogue; no balances loaded, no rewards unlocked."
            )
        elif name == "PIN & Security":
            status = "Parent PIN configured" if has_pin() else "No Parent PIN configured"
            self._section_description.setText(
                f"{status}. Parent Corner is currently unlocked. "
                "Lock and Return Home to secure it. PIN values are never displayed."
            )
        else:
            self._section_description.setText(name + " — read-only preview; controls not yet connected.")
        return True

    def return_home(self):
        self._unlocked = False
        self._pin.clear()
        self._stack.setCurrentWidget(self._child_home if self._chooser.selected_username() else self._home)

    def _show_parent(self):
        self._unlocked = False
        self._pin.clear()
        self._parent_message.setText("Enter your existing Eden parent PIN to unlock.")
        self._stack.setCurrentWidget(self._parent)
        self._pin.setFocus()

    def unlock_parent(self, pin):
        if not has_pin() or not verify_pin(pin):
            self._parent_message.setText("Parent Corner remains locked.")
            return False
        self._unlocked = True
        card = self._chooser.selected_public_card()
        selected_name = card["display_name"] if card else "No child selected"
        self._parent_child_label.setText("Selected child: " + selected_name)
        self._section_description.setText("Select a section. Controls are read-only in this prototype.")
        self._stack.setCurrentWidget(self._dashboard)
        return True

    def _unlock_from_entry(self):
        self.unlock_parent(self._pin.text())
        self._pin.clear()

def main():
    application = QApplication(sys.argv)
    window = EdenNativeWindow()
    window.show()
    return application.exec()

if __name__ == "__main__":
    raise SystemExit(main())
