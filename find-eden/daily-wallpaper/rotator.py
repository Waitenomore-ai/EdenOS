#!/usr/bin/env python3
"""Find Eden wallpaper rotation. No desktop changes unless --apply or --watch."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

EPOCH = dt.date(2026, 10, 31)

def load_manifest(manifest):
    manifest = Path(manifest).resolve()
    try:
        rows = json.loads(manifest.read_text())
        if not isinstance(rows, list) or not rows: raise ValueError('Manifest must be a nonempty list')
        images, ids, files = [], set(), set()
        for row in rows:
            if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip() for k in ('id','title','file')): raise ValueError('Invalid manifest entry')
            relative = Path(row['file'])
            target = (manifest.parent / relative).resolve()
            if relative.is_absolute() or '..' in relative.parts or not target.is_relative_to(manifest.parent) or target.suffix.lower() not in ('.png','.jpg','.jpeg','.webp') or not target.is_file(): raise ValueError('Invalid or missing image: '+row['file'])
            if row['id'] in ids or target in files: raise ValueError('Duplicate image or ID')
            ids.add(row['id']); files.add(target); images.append(target)
        return images
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        raise ValueError('Cannot read valid wallpaper manifest') from exc

def choose(images, day):
    return images[(day-EPOCH).days % len(images)]

def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.eden-')
    try:
        with os.fdopen(fd,'w') as out:
            json.dump(data,out,indent=2); out.flush(); os.fsync(out.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)

def command(args, run):
    return run(['xfconf-query','-c','xfce4-desktop']+args, check=True, capture_output=True, text=True).stdout.rstrip('\n')

def apply(image, state, run=subprocess.run):
    props = command(['-l'],run).splitlines()
    targets = [p for p in props if p.startswith('/backdrop/') and p.rsplit('/',1)[-1] in ('last-image','image-path')]
    if not targets: raise ValueError('No XFCE wallpaper properties found; log into XFCE first')
    backup = state.with_name('backup.json')
    saved = json.loads(backup.read_text()) if backup.exists() else (json.loads(state.read_text()) if state.exists() else {'previous':{}})
    previous = dict(saved['previous'])
    updates = {}
    for prop in targets:
        updates[prop] = str(image)
        sibling = prop.rsplit('/',1)[0]+'/image-style'
        # XFCE SCALED=4 preserves the full image; ZOOMED=5 crops it.
        if sibling in props: updates[sibling]='4'
    # Read every original before changing anything. Preserve the first backup.
    current = {p:command(['-p',p],run) for p in updates}
    for prop,value in current.items(): previous.setdefault(prop,value)
    atomic_json(backup, {'previous':previous})
    for prop,value in updates.items():
        if current[prop] != value: command(['-p',prop,'-s',value],run)
    atomic_json(state, {'previous':previous,'image':str(image),'date':dt.date.today().isoformat()})

def restore(state, run=subprocess.run):
    backup=state.with_name('backup.json')
    source=backup if backup.exists() else state
    if not source.exists(): return
    data=json.loads(source.read_text()); props=command(['-l'],run).splitlines()
    for prop,value in data['previous'].items():
        if prop in props and prop.startswith('/backdrop/') and prop.rsplit('/',1)[-1] in ('last-image','image-path','image-style'):
            command(['-p',prop,'-s',value],run)

def xfce_session():
    """Identify this display's XFCE session process without another dependency."""
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit(): continue
        try:
            if proc.stat().st_uid != os.getuid() or (proc/'comm').read_text().strip() != 'xfce4-session': continue
            environment=(proc/'environ').read_bytes().split(b'\0')
            if ('DISPLAY='+os.environ.get('DISPLAY','')).encode() in environment:
                return proc/'stat', (proc/'stat').read_text().split()[21]
        except (OSError,IndexError): continue
    return None

def session_alive(session):
    if session is None: return False
    try: return session[0].read_text().split()[21] == session[1]
    except (OSError,IndexError): return False

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=Path(__file__).resolve().parent.parent/'wallpapers.json')
    parser.add_argument('--state',type=Path,default=Path(os.environ.get('XDG_STATE_HOME',str(Path.home()/'.local/state')))/'find-eden/state.json')
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--poke',action='store_true'); modes.add_argument('--apply',action='store_true'); modes.add_argument('--watch',action='store_true'); modes.add_argument('--restore',action='store_true'); modes.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    if args.poke:
        args.state.parent.mkdir(parents=True,exist_ok=True)
        (args.state.parent/'refresh').touch()
        return 0
    if not (args.apply or args.watch or args.restore):
        print(choose(load_manifest(args.manifest),dt.date.today())); return
    args.state.parent.mkdir(parents=True,exist_ok=True)
    # The long-lived watcher has a separate lock; per-update locking also excludes timer races.
    watcher=None
    session=xfce_session() if args.watch else None
    if args.watch:
        if session is None:
            print('Find Eden: cannot identify this XFCE session; no wallpaper changes made. Start from an XFCE login.',file=sys.stderr)
            return 1
        lock_name='watch-'+(session[0].parent.name if session else 'default')+'.lock'
        watcher=open(args.state.parent/lock_name,'a')
        try: fcntl.flock(watcher,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: return
        with open(args.state.parent/'update.lock','a') as registration:
            fcntl.flock(registration,fcntl.LOCK_EX)
            if (args.state.parent/'uninstalling').exists(): return 0
            proc=os.readlink('/proc/self')
            start=Path('/proc/self/stat').read_text().split()[21]
            atomic_json(args.state.parent/('watcher-'+str(os.getpid())+'.json'),{'pid':os.getpid(),'proc':proc,'start':start})
    last_day=None
    while True:
        if args.watch and not session_alive(session): return 0
        try:
            with open(args.state.parent/'update.lock','a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                if not args.restore and (args.state.parent/'uninstalling').exists():
                    print('Find Eden: installation is being removed; no wallpaper changes made.',file=sys.stderr)
                    return 1
                if args.restore: restore(args.state)
                elif not args.watch or last_day != dt.date.today() or (args.state.parent/'refresh').exists():
                    apply(choose(load_manifest(args.manifest),dt.date.today()),args.state)
                    last_day=dt.date.today()
                    (args.state.parent/'refresh').unlink(missing_ok=True)
        except (OSError,ValueError,KeyError,subprocess.SubprocessError) as exc:
            print('Find Eden: '+str(exc),file=sys.stderr)
            if not args.watch: return 1
        if not args.watch: return 0
        time.sleep(60)

if __name__=='__main__': sys.exit(main())
