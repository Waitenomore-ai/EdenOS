import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

class InstallTests(unittest.TestCase):
    def test_install_is_self_contained_and_uninstall_removes_only_own_files(self):
        with tempfile.TemporaryDirectory(prefix='eden space ') as tmp:
            root=Path(tmp); pack=root/'pack'; (pack/'daily-wallpaper').mkdir(parents=True)
            import shutil
            for file in ('rotator.py','install.py'): shutil.copy(Path(__file__).parent/file,pack/'daily-wallpaper'/file)
            (pack/'image.png').write_bytes(b'png')
            (pack/'wallpapers.json').write_text(json.dumps([dict(id='1',title='a',file='image.png')]))
            env=dict(os.environ,HOME=str(root/'home'),XDG_DATA_HOME=str(root/'data'),XDG_CONFIG_HOME=str(root/'config'),XDG_STATE_HOME=str(root/'state'))
            result=subprocess.run([sys.executable,str(pack/'daily-wallpaper/install.py'),'--no-start'],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            copied=root/'data/find-eden/wallpapers.json'; self.assertTrue(copied.exists())
            result=subprocess.run([sys.executable,str(root/'data/find-eden/daily-wallpaper/rotator.py'),'--dry-run'],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr); self.assertEqual(result.stdout.strip(),str(root/'data/find-eden/image.png'))
            result=subprocess.run([sys.executable,str(pack/'daily-wallpaper/install.py'),'--uninstall','--no-start'],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(copied.exists()); self.assertFalse((root/'config/autostart/find-eden.desktop').exists())

    def fixture(self, root):
        import shutil
        pack=root/'pack'; (pack/'daily-wallpaper').mkdir(parents=True)
        for name in ('rotator.py','install.py'): shutil.copy(Path(__file__).parent/name,pack/'daily-wallpaper'/name)
        (pack/'image.png').write_bytes(b'png')
        (pack/'wallpapers.json').write_text(json.dumps([dict(id='1',title='a',file='image.png')]))
        env=dict(os.environ,HOME=str(root/'home'),XDG_DATA_HOME=str(root/'data'),XDG_CONFIG_HOME=str(root/'config'),XDG_STATE_HOME=str(root/'state'))
        bindir=root/'bin'; bindir.mkdir()
        xfconf=bindir/'xfconf-query'
        xfconf.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
path=pathlib.Path(os.environ['TEST_PROPS'])
props=json.loads(path.read_text())
a=sys.argv
if '-l' in a: print('\\n'.join(props))
elif '-s' in a:
    if os.environ.get('TEST_FAIL_WRITE'): sys.exit(1)
    props[a[a.index('-p')+1]]=a[-1]; path.write_text(json.dumps(props))
else: print(props[a[a.index('-p')+1]])
'''); xfconf.chmod(0o755)
        systemctl=bindir/'systemctl'; systemctl.write_text('#!/bin/sh\nexit 0\n'); systemctl.chmod(0o755)
        props=root/'props.json'; props.write_text(json.dumps({'/backdrop/screen0/last-image':'wallpaper-A.png'}))
        env.update(PATH=str(bindir)+os.pathsep+os.environ['PATH'],TEST_PROPS=str(props))
        return pack,env,props

    def invoke(self, pack, env, *args):
        return subprocess.run([sys.executable,str(pack/'daily-wallpaper/install.py'),*args],env=env,capture_output=True,text=True)

    def rotate(self, root, env):
        result=subprocess.run([sys.executable,str(root/'data/find-eden/daily-wallpaper/rotator.py'),'--apply'],env=env,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_failed_restore_preserves_installed_images_and_returns_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); pack,env,props=self.fixture(root)
            self.assertEqual(self.invoke(pack,env,'--no-start').returncode,0)
            self.rotate(root,env)
            result=self.invoke(pack,dict(env,TEST_FAIL_WRITE='1'),'--uninstall')
            self.assertNotEqual(result.returncode,0)
            self.assertTrue((root/'data/find-eden/image.png').exists())
            self.assertTrue((root/'config/autostart/find-eden.desktop').exists())

    def test_reinstall_backs_up_new_wallpaper_and_archives_old_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); pack,env,props=self.fixture(root)
            self.assertEqual(self.invoke(pack,env,'--no-start').returncode,0)
            self.rotate(root,env)
            self.assertEqual(self.invoke(pack,env,'--uninstall').returncode,0)
            props.write_text(json.dumps({'/backdrop/screen0/last-image':'wallpaper-B.png'}))
            self.assertEqual(self.invoke(pack,env,'--no-start').returncode,0)
            self.rotate(root,env)
            self.assertEqual(self.invoke(pack,env,'--uninstall').returncode,0)
            self.assertEqual(json.loads(props.read_text())['/backdrop/screen0/last-image'],'wallpaper-B.png')
            archives=list((root/'state/find-eden').glob('recovery-*'))
            self.assertTrue(archives)
            self.assertEqual(json.loads((archives[0]/'backup.json').read_text())['previous']['/backdrop/screen0/last-image'],'wallpaper-A.png')

    def test_uninstall_refuses_unowned_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); pack,env,props=self.fixture(root)
            target=root/'data/find-eden'; target.mkdir(parents=True)
            (target/'personal.txt').write_text('keep')
            result=self.invoke(pack,env,'--uninstall','--no-start')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((target/'personal.txt').read_text(),'keep')

    def test_uninstall_serializes_and_stops_all_owned_watchers_only(self):
        import fcntl
        import time
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); pack,env,props=self.fixture(root)
            self.assertEqual(self.invoke(pack,env,'--no-start').returncode,0)
            self.rotate(root,env)
            state=root/'state/find-eden'; script=root/'data/find-eden/daily-wallpaper/rotator.py'
            children=[]
            try:
                for owned in (True,True,False):
                    record=state/('watcher-test-'+str(len(children))+'.json')
                    code="import json,os,pathlib,sys,time; proc=os.readlink('/proc/self'); start=pathlib.Path('/proc',proc,'stat').read_text().split()[21]; pathlib.Path(sys.argv[1]).write_text(json.dumps({'pid':os.getpid(),'proc':proc,'start':start})); time.sleep(30)"
                    argv=[sys.executable,'-c',code,str(record)]
                    if owned: argv += [str(script),'--watch']
                    proc=subprocess.Popen(argv); children.append(proc)
                    for attempt in range(100):
                        if record.exists(): break
                        time.sleep(.01)
                    self.assertTrue(record.exists())
                with open(state/'update.lock','a') as lock:
                    fcntl.flock(lock,fcntl.LOCK_EX)
                    uninstall=subprocess.Popen([sys.executable,str(pack/'daily-wallpaper/install.py'),'--uninstall'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                    time.sleep(.15)
                    self.assertIsNone(uninstall.poll(),'uninstall must wait for an in-flight wallpaper update')
                    fcntl.flock(lock,fcntl.LOCK_UN)
                stdout,stderr=uninstall.communicate(timeout=10)
                self.assertEqual(uninstall.returncode,0,stderr)
                self.assertIsNotNone(children[0].poll())
                self.assertIsNotNone(children[1].poll())
                self.assertIsNone(children[2].poll(),'unrelated process must survive')
                self.assertEqual(json.loads(props.read_text())['/backdrop/screen0/last-image'],'wallpaper-A.png')
                self.assertTrue((state/'uninstalling').exists())
                blocked=subprocess.run([sys.executable,str(pack/'daily-wallpaper/rotator.py'),'--apply'],env=env,capture_output=True,text=True)
                self.assertNotEqual(blocked.returncode,0)
                self.assertEqual(json.loads(props.read_text())['/backdrop/screen0/last-image'],'wallpaper-A.png')
            finally:
                for child in children:
                    if child.poll() is None: child.terminate()
                    child.wait()
