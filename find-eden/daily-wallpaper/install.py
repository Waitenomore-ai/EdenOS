#!/usr/bin/env python3
"""Run locally in the Eden OS XFCE user's terminal. Never needs sudo."""
import argparse
import os
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import fcntl
import time
import rotator

def json_marker(path):
    try: return json.loads(path.read_text())
    except (OSError,ValueError): return None

def stop_watchers(state, script):
    """Only signal records matching UID, PID namespace, start time, and owned argv."""
    records=list(state.glob('watcher-*.json'))
    for record in records:
        try:
            data=json.loads(record.read_text())
            pid=int(data['pid']); proc_name=str(data.get('proc',pid))
            if pid <= 1 or not proc_name.isdigit(): continue
            proc=Path('/proc')/proc_name
            def matches():
                try:
                    stat=(proc/'stat').read_text().split()
                    args=(proc/'cmdline').read_bytes().split(b'\0')
                    status=(proc/'status').read_text().splitlines()
                    ns=[line for line in status if line.startswith('NSpid:')]
                    return (proc.stat().st_uid == os.getuid() and stat[21] == data['start'] and stat[2] != 'Z'
                            and ns and int(ns[0].split()[-1]) == pid
                            and str(script).encode() in args and b'--watch' in args)
                except (OSError,ValueError,IndexError): return False
            if not matches(): continue
            # pidfd pins the verified process against PID reuse during termination.
            descriptor=os.pidfd_open(pid)
            try:
                if not matches(): continue
                signal.pidfd_send_signal(descriptor,signal.SIGTERM)
                deadline=time.monotonic()+3
                while matches() and time.monotonic()<deadline: time.sleep(.02)
                if matches(): raise ValueError('Wallpaper watcher did not stop; installation retained')
            finally: os.close(descriptor)
            record.unlink(missing_ok=True)
        except ProcessLookupError: continue
        except (KeyError,json.JSONDecodeError): continue
        except OSError as exc:
            raise ValueError('Cannot verify or stop wallpaper watcher; installation retained: '+str(exc)) from exc

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--uninstall',action='store_true')
    parser.add_argument('--no-start',action='store_true',help='prepare/remove files without interacting with a desktop or systemd')
    args=parser.parse_args()
    source=Path(__file__).resolve().parent.parent
    home=Path.home()
    destination=Path(os.environ.get('XDG_DATA_HOME',str(home/'.local/share')))/'find-eden'
    config=Path(os.environ.get('XDG_CONFIG_HOME',str(home/'.config')))
    state=Path(os.environ.get('XDG_STATE_HOME',str(home/'.local/state')))/'find-eden'
    units=config/'systemd/user'; autostart=config/'autostart/find-eden.desktop'
    def systemctl(*items):
        try: return subprocess.run(['systemctl','--user',*items],check=False,capture_output=True).returncode==0
        except OSError: return False
    marker=destination/'.find-eden-install.json'
    ownership={'application':'find-eden-daily-wallpaper','version':1,'destination':str(destination.resolve())}
    if args.uninstall:
        if destination.is_symlink() or not marker.is_file() or json_marker(marker) != ownership:
            raise ValueError('Refusing to uninstall an unowned directory: '+str(destination))
        state.mkdir(parents=True,exist_ok=True)
        with open(state/'update.lock','a') as update_lock:
            fcntl.flock(update_lock,fcntl.LOCK_EX)
            # Every update and watcher registration checks this flag while holding this lock.
            (state/'uninstalling').touch()
            if not args.no_start:
                systemctl('disable','--now','find-eden.timer')
                stop_watchers(state,destination/'daily-wallpaper/rotator.py')
                try: rotator.restore(state/'state.json')
                except Exception as exc:
                    raise ValueError('Wallpaper restore failed; installation and images retained. Log into XFCE and retry uninstall: '+str(exc)) from exc
            autostart.unlink(missing_ok=True)
            for name in ('find-eden.service','find-eden.timer'): (units/name).unlink(missing_ok=True)
            if destination.exists(): shutil.rmtree(destination)
            if not args.no_start: systemctl('daemon-reload')
        print('Removed Find Eden startup files. Wallpaper backup retained at '+str(state/'backup.json'))
        return
    images=rotator.load_manifest(source/'wallpapers.json')
    fresh=source != destination
    if fresh:
        if destination.exists(): raise ValueError('Already installed. Uninstall first; your backup will be retained.')
        destination.mkdir(parents=True)
        shutil.copy2(source/'wallpapers.json',destination/'wallpapers.json')
        for image in images:
            relative=image.relative_to(source); target=destination/relative
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(image,target)
        (destination/'daily-wallpaper').mkdir()
        for name in ('rotator.py','install.py'): shutil.copy2(source/'daily-wallpaper'/name,destination/'daily-wallpaper'/name)
    script=destination/'daily-wallpaper/rotator.py'
    # systemd escaping is distinct from Desktop Entry Exec escaping.
    def unit_quote(value): return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
    def desktop_quote(value): return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')+'"'
    units.mkdir(parents=True,exist_ok=True); autostart.parent.mkdir(parents=True,exist_ok=True)
    (units/'find-eden.service').write_text('[Unit]\nDescription=Queue Find Eden daily wallpaper refresh\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 '+unit_quote(script)+' --poke\n')
    (units/'find-eden.timer').write_text('[Unit]\nDescription=Find Eden daily wallpaper\n[Timer]\nOnCalendar=*-*-* 00:00:00\nPersistent=true\n[Install]\nWantedBy=timers.target\n')
    autostart.write_text('[Desktop Entry]\nType=Application\nName=Find Eden daily wallpaper\nExec=/usr/bin/python3 '+desktop_quote(script)+' --watch\nOnlyShowIn=XFCE;\nTerminal=false\n')
    if fresh:
        # Preserve recovery data, then let the new installation capture its own originals.
        retained=[state/name for name in ('backup.json','state.json') if (state/name).exists()]
        if retained:
            archive=Path(tempfile.mkdtemp(prefix='recovery-',dir=state))
            for previous in retained: shutil.copy2(previous,archive/previous.name)
            for previous in retained: previous.unlink()
        rotator.atomic_json(marker,ownership)
        (state/'uninstalling').unlink(missing_ok=True)
    elif not marker.is_file() or json_marker(marker) != ownership:
        raise ValueError('Installation ownership marker is missing or invalid')
    if not args.no_start:
        if not os.environ.get('DISPLAY') or not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
            print('Prepared. Log into XFCE to start rotation. Run the installer again there to enable the optional timer.')
            return
        systemctl('daemon-reload'); systemctl('enable','--now','find-eden.timer')
        state.mkdir(parents=True,exist_ok=True)
        proc=subprocess.Popen(['/usr/bin/python3',str(script),'--watch'],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    print('Installed. XFCE login starts daily rotation; no-start defers activation until login.' if args.no_start else 'Installed. Daily rotation starts in the current XFCE session.')

if __name__=='__main__':
    try: main()
    except (OSError,ValueError) as exc: print(str(exc),file=sys.stderr); sys.exit(1)
