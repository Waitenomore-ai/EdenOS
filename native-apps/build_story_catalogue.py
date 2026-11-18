"""Extract only the preserved iMac BOOKS expression, without importing GTK or executing shelf code."""
import ast, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent / 'imac-source'

def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

collection = load_module('story_collection')
butterfly = load_module('butterfly_story')
scenes = load_module('story_garden_model')
tree = ast.parse((ROOT / 'story_shelf.py').read_text())
expr = next(node.value for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'BOOKS' for target in node.targets))
# Strict AST allowlist: no attributes, imports, subscripts or arbitrary function calls.
allowed = (ast.Expression, ast.BinOp, ast.Add, ast.Tuple, ast.Constant, ast.Name, ast.Load, ast.Call, ast.GeneratorExp, ast.comprehension, ast.Attribute, ast.Store)
for node in ast.walk(expr):
    if not isinstance(node, allowed):
        raise ValueError('Unexpected source expression: ' + type(node).__name__)
    if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or node.func.id not in {'PictureStory', 'tuple'}):
        raise ValueError('Unexpected call')
    if isinstance(node, ast.Attribute) and (node.attr != 'sentence' or not isinstance(node.value, ast.Name) or node.value.id != 'scene'):
        raise ValueError('Unexpected attribute')
    if isinstance(node, ast.Name) and node.id not in {'PictureStory','tuple','scene','SCENES','STORIES','BUTTERFLY_TITLE','BUTTERFLY_COVER','BUTTERFLY_PAGES'}:
        raise ValueError('Unexpected name: ' + node.id)
books = eval(compile(ast.Expression(expr), '<approved-books-expression>', 'eval'), {'__builtins__': {}}, {
    'PictureStory': collection.PictureStory, 'tuple': tuple,
    'SCENES': scenes.SCENES, 'STORIES': collection.STORIES,
    'BUTTERFLY_TITLE': butterfly.TITLE, 'BUTTERFLY_COVER': butterfly.COVER, 'BUTTERFLY_PAGES': butterfly.PAGES,
})
assert len({b.title for b in books}) == len(books)
assert all(b.pages and all(isinstance(p, str) and p.strip() for p in b.pages) for b in books)
out = Path(__file__).resolve().parent / 'assets' / 'stories' / 'imac_preserved_catalogue.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps([{'title': b.title, 'cover': b.image, 'pages': list(b.pages)} for b in books], ensure_ascii=False, indent=2) + '\n')
print('EXTRACTED_BOOKS', len(books), 'PAGES', sum(len(b.pages) for b in books), 'DESTINATION', out)
