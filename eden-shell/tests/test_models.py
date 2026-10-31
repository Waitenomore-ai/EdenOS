import importlib
from importlib.resources import files
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


def load_module(test_case, module_name):
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        test_case.fail(f"required Eden module is missing: {module_name} ({exc})")


class CatalogueTests(unittest.TestCase):
    def test_catalogue_defines_all_home_categories_and_defaults_empty(self):
        catalogue = load_module(self, "eden_shell.catalogue")
        self.assertEqual(
            [category.slug for category in catalogue.CATEGORIES],
            ["learn", "play", "read", "create"],
        )
        self.assertEqual(
            [activity.id for activity in catalogue.load_catalogue()],
            ["tux-paint", "number-meadow", "word-woodland", "story-garden", "art-studio", "puzzle-pond", "time-routines", "nature-explorer", "feelings-quiet-space"],
        )
        self.assertEqual(catalogue.load_catalogue(Path("/no/such/eden-catalogue.json")), ())

    def test_home_categories_use_included_original_icons(self):
        catalogue = load_module(self, "eden_shell.catalogue")
        package_data = files("eden_shell").joinpath("data", "icons")
        for category in catalogue.CATEGORIES:
            self.assertEqual(category.icon, category.slug)
            self.assertTrue(package_data.joinpath(f"{category.slug}.svg").is_file())

    def test_catalogue_accepts_only_reviewed_local_activities_with_safe_desktop_ids(self):
        catalogue = load_module(self, "eden_shell.catalogue")
        entries = [
            {
                "id": "math-bubbles",
                "title": "Number Bubbles",
                "description": "Practise counting.",
                "category": "learn",
                "desktop_id": "number-bubbles.desktop",
                "offline": True,
                "reviewed": True,
            },
            {
                "id": "unsafe-command",
                "title": "Unsafe",
                "description": "Must not launch shell commands.",
                "category": "play",
                "command": "sh -c 'touch /tmp/eden'",
                "offline": True,
                "reviewed": True,
            },
            {
                "id": "unreviewed",
                "title": "Unreviewed",
                "description": "Hidden until reviewed.",
                "category": "read",
                "desktop_id": "unreviewed.desktop",
                "offline": True,
                "reviewed": False,
            },
            {
                "id": "bad-desktop-id",
                "title": "Bad target",
                "description": "Contains path traversal.",
                "category": "create",
                "desktop_id": "../../etc/passwd",
                "offline": True,
                "reviewed": True,
            },
            {
                "id": "bad-category-type",
                "title": "Bad category",
                "description": "A broken record must be ignored.",
                "category": [],
                "desktop_id": "broken.desktop",
                "offline": True,
                "reviewed": True,
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activities.json"
            path.write_text(json.dumps(entries), encoding="utf-8")
            try:
                loaded = catalogue.load_catalogue(path)
            except TypeError:
                self.fail("malformed category data should be ignored, not crash the launcher")
        self.assertEqual([activity.id for activity in loaded], ["math-bubbles"])
        self.assertFalse(hasattr(loaded[0], "command"))


class PreferencesTests(unittest.TestCase):
    def test_accessibility_preferences_default_to_safe_local_values(self):
        preferences = load_module(self, "eden_shell.preferences")
        with tempfile.TemporaryDirectory() as directory:
            current = preferences.load_preferences(Path(directory) / "new.json")
        self.assertEqual(current.text_scale, 1.0)
        self.assertFalse(current.high_contrast)
        self.assertFalse(current.reduced_motion)

    def test_accessibility_preferences_round_trip_locally(self):
        preferences = load_module(self, "eden_shell.preferences")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            requested = preferences.AccessibilityPreferences(
                text_scale=1.3, high_contrast=True, reduced_motion=True
            )
            preferences.save_preferences(requested, path)
            actual = preferences.load_preferences(path)
        self.assertEqual(actual, requested)

    def test_invalid_preferences_fall_back_without_enabling_features(self):
        preferences = load_module(self, "eden_shell.preferences")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(
                '{"text_scale":99,"high_contrast":"yes","reduced_motion":false}',
                encoding="utf-8",
            )
            actual = preferences.load_preferences(path)
        self.assertEqual(actual.text_scale, 1.0)
        self.assertFalse(actual.high_contrast)
        self.assertFalse(actual.reduced_motion)

    def test_accessibility_presets_are_named_and_safe(self):
        preferences = load_module(self, "eden_shell.preferences")
        self.assertEqual(preferences.accessibility_preset("calm"), preferences.AccessibilityPreferences())
        self.assertEqual(preferences.accessibility_preset("clear-large"), preferences.AccessibilityPreferences(1.3, False, True))
        self.assertEqual(preferences.accessibility_preset("high-contrast"), preferences.AccessibilityPreferences(1.2, True, True))
        self.assertEqual(preferences.accessibility_preset("unknown"), preferences.AccessibilityPreferences())


class BrowserPilotTests(unittest.TestCase):
    def test_kidstube_shortcut_uses_deny_by_default_firefox_policy(self):
        root = Path(__file__).parents[2]
        policy_path = root / "config/includes.chroot/etc/firefox/policies/policies.json"
        policy_document = json.loads(policy_path.read_text(encoding="utf-8"))
        policy = policy_document["policies"]
        browser = load_module(self, "eden_shell.browser")
        self.assertTrue(browser.kidstube_policy_ready(policy_path))
        filter_policy = policy["WebsiteFilter"]
        self.assertEqual(filter_policy["Block"], ["<all_urls>"])
        self.assertIn("https://www.kids-tube.com/*", filter_policy["Exceptions"])
        self.assertFalse(any("youtube.com/*" in item for item in filter_policy["Exceptions"]))
        self.assertTrue(policy["DisableDeveloperTools"])
        self.assertTrue(policy["DisableTelemetry"])
        self.assertTrue(policy["SanitizeOnShutdown"])

        desktop = (
            root / "config/includes.chroot/etc/skel/Desktop/KidsTube.desktop"
        ).read_text(encoding="utf-8")
        self.assertIn("Exec=/usr/local/bin/eden-kidstube", desktop)
        child_session = (
            root / "config/includes.chroot/usr/local/bin/eden-child-session"
        ).read_text(encoding="utf-8")
        self.assertIn("xfwm4 --replace", child_session)
        launcher = (
            root / "config/includes.chroot/usr/local/bin/eden-kidstube"
        ).read_text(encoding="utf-8")
        launch_module = (root / "eden-shell/eden_shell/kidstube.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("eden_shell.kidstube", launcher)
        self.assertIn("--new-window", launch_module)

    def test_browser_policy_validation_fails_closed_for_missing_or_broadened_policy(self):
        browser = load_module(self, "eden_shell.browser")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policies.json"
            self.assertFalse(browser.kidstube_policy_ready(path))
            path.write_text(
                json.dumps(
                    {
                        "policies": {
                            "WebsiteFilter": {
                                "Block": ["<all_urls>"],
                                "Exceptions": ["https://*/*"],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            self.assertFalse(browser.kidstube_policy_ready(path))


class SetupModelTests(unittest.TestCase):
    def test_adult_setup_launcher_and_polkit_agent_are_included(self):
        root = Path(__file__).parents[2]
        desktop = (
            root / "config/includes.chroot/usr/share/applications/eden-setup.desktop"
        ).read_text(encoding="utf-8")
        launcher = (
            root / "config/includes.chroot/usr/local/bin/eden-setup"
        ).read_text(encoding="utf-8")
        packages = (root / "config/package-lists/eden.list.chroot_install").read_text(
            encoding="utf-8"
        )
        agent = (
            root / "config/includes.chroot/etc/xdg/autostart/eden-polkit-agent.desktop"
        ).read_text(encoding="utf-8")
        self.assertIn("Exec=/usr/local/bin/eden-setup", desktop)
        self.assertIn("eden_shell.setup", launcher)
        self.assertIn("accountsservice", packages)
        self.assertIn("mate-polkit", packages)
        self.assertIn("/usr/libexec/polkit-mate-authentication-agent-1", agent)

    def test_child_passphrase_is_hashed_via_stdin_not_process_arguments(self):
        crypto = load_module(self, "eden_shell.setup_crypto")
        with patch(
            "subprocess.run",
            return_value=SimpleNamespace(stdout="$6$randomsalt$hashvalue\n"),
        ) as run:
            hashed = crypto.hash_password("a remembered phrase")
        args, options = run.call_args
        self.assertEqual(args[0], ["/usr/bin/openssl", "passwd", "-6", "-stdin"])
        self.assertNotIn("a remembered phrase", args[0])
        self.assertEqual(options["input"], "a remembered phrase\n")
        self.assertTrue(hashed.startswith("$6$"))

    def test_child_profile_input_needs_only_nickname_username_and_password(self):
        model = load_module(self, "eden_shell.setup_model")
        profile = model.validate_child_profile(
            "  Sam  ", "sam_learning", "play at home", "play at home"
        )
        self.assertEqual(profile.nickname, "Sam")
        self.assertEqual(profile.username, "sam_learning")
        self.assertNotIn("password", profile.__dict__)

    def test_child_profile_validation_rejects_bad_username_or_password(self):
        model = load_module(self, "eden_shell.setup_model")
        for username in ("", "Sam", "admin user", "../sam", "-sam"):
            with self.subTest(username=username), self.assertRaises(ValueError):
                model.validate_child_profile(
                    "Sam", username, "long password", "long password"
                )
        with self.assertRaises(ValueError):
            model.validate_child_profile("Sam", "sam", "short", "short")
        with self.assertRaises(ValueError):
            model.validate_child_profile(
                "Sam", "sam", "long password", "different"
            )


class NavigationTests(unittest.TestCase):
    def test_home_category_progress_and_help_navigation(self):
        navigation = load_module(self, "eden_shell.navigation")
        state = navigation.ScreenState()
        self.assertEqual(state.page, "home")
        state.open_category("learn")
        self.assertEqual(state.page, "category")
        self.assertEqual(state.category, "learn")
        state.open_progress()
        self.assertEqual(state.page, "progress")
        state.open_help()
        self.assertEqual(state.page, "help")
        state.go_home()
        self.assertEqual(state.page, "home")
        self.assertIsNone(state.category)

    def test_unknown_category_is_rejected(self):
        navigation = load_module(self, "eden_shell.navigation")
        with self.assertRaises(ValueError):
            navigation.ScreenState().open_category("adult-settings")


if __name__ == "__main__":
    unittest.main()

