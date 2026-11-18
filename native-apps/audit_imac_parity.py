"""Read-only implementation parity audit; not a visual screenshot comparison."""
import ast, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAC = ROOT.parent / 'imac-source'
NATIVE = ROOT / 'eden_native' / 'qt_app.py'

CANONICAL = {
    'Number Meadow': ('number_meadow.py', 'number_meadow_model.py'),
    'Word Woodland': ('word_woodland.py', 'word_woodland_model.py'),
    'Puzzle Pond': ('puzzle_pond.py', 'puzzle_pond_model.py'),
    'Art Studio': ('art_studio.py', 'art_studio_model.py'),
    'Nature Explorer': ('nature_explorer.py', 'nature_explorer_model.py'),
    'My Day': ('time_routines.py', 'time_routines_model.py'),
    'Feelings': ('feelings.py', 'feelings_model.py'),
    'Story Garden': ('story_garden.py', 'story_garden_model.py'),
}

text = NATIVE.read_text()
report = {'scope': 'Static source comparison only; no claim of visual or behavioural equivalence', 'screens': []}
for title, (screen, model) in CANONICAL.items():
    imac_screen = IMAC / screen
    imac_model = IMAC / model
    native_model = ROOT / 'eden_native' / 'approved_models' / model
    import hashlib
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    report['screens'].append({
        'name': title,
        'canonical_ui_exists': imac_screen.is_file(),
        'canonical_model_exists': imac_model.is_file(),
        'native_model_byte_identical': digest(imac_model) == digest(native_model) if digest(imac_model) else False,
        'native_title_present': title in text,
        'native_gtk_layout_ported': False,
        'visual_parity_verified': False,
    })
report['known_differences'] = [
    'iMac activity windows are GTK4 fullscreen and undecorated; native preview is a decorated 1024x768 Qt window',
    'iMac has centred shared Home/title toolbar; native Qt preview uses a generic Eden OS title and activity buttons',
    'iMac scene-specific CSS artwork and layout are not yet recreated in Qt',
    'Native Story Garden contains 63 text drafts, not 75 final approved books',
    'Native Art Studio has free sticker placement and drawing, but not full iMac layer and Garden Stars behaviour',
    'No real iMac-vs-native screenshot comparison has been completed',
]
output = ROOT.parent / 'releases' / 'EDEN_IMAC_PARITY_AUDIT_20261118.json'
output.write_text(json.dumps(report, indent=2) + '\n')
print('PARITY_AUDIT', output)
print('MODEL_MATCHES', sum(x['native_model_byte_identical'] for x in report['screens']), '/', len(report['screens']))
print('VISUAL_VERIFIED', sum(x['visual_parity_verified'] for x in report['screens']), '/', len(report['screens']))
