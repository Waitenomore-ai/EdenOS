"""Bundle the inspected wallpaper scenes into one offline game."""
import base64
import hashlib
import json
import argparse
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
def build(embed=False):
    scenes=json.loads((ROOT/'src/scenes.json').read_text())
    for scene in scenes:
        relative=scene.get('asset_path','wallpapers/'+scene['file'])
        file=(ROOT/relative).resolve()
        assert file.is_relative_to(ROOT), 'Wallpaper path escapes the pack'
        with Image.open(file) as image:
            assert image.size==(scene['width'],scene['height']), f'Unexpected dimensions for {file.name}'
        scene['image']=('data:image/png;base64,'+base64.b64encode(file.read_bytes()).decode()) if embed else relative
    game=(ROOT/'src/game.js').read_text()
    boot='FindEden.mount('+json.dumps(scenes,separators=(',',':'))+');'
    hashes=' '.join("'sha256-"+base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()+"'" for s in [game,boot])
    csp="default-src 'none'; script-src "+hashes+"; style-src 'unsafe-inline'; img-src data: 'self' file:; connect-src 'none'; base-uri 'none'; form-action 'none'"
    html=(ROOT/'src/index.html').read_text()
    for key,value in {'__CSP__':csp,'__STYLE__':(ROOT/'src/style.css').read_text(),'__GAME__':game,'__BOOT__':boot}.items():
        html=html.replace(key,value)
    path=ROOT/'Find-Eden.html';path.write_text(html)
    print(f'Built {path.name}: {path.stat().st_size:,} bytes, {len(scenes)} full-resolution scenes')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--embed',action='store_true',help='embed all images; default uses bundled local files for faster loading')
    build(parser.parse_args().embed)
