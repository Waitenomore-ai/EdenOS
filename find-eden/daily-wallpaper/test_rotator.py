import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
import rotator

class RotationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ('one space.png', 'two.png', 'three.png'): (self.root/name).write_bytes(b'png')
        self.manifest = self.root/'wallpapers.json'
        self.entries = [dict(id=str(i), title=name, file=name) for i,name in enumerate(('one space.png','two.png','three.png'))]
        self.manifest.write_text(json.dumps(self.entries))
    def test_watch_without_identified_session_makes_no_wallpaper_changes(self):
        from unittest.mock import patch
        state=self.root/'session-state/state.json'
        with patch.object(rotator,'xfce_session',return_value=None), patch.object(rotator.sys,'argv',['rotator.py','--watch','--state',str(state)]):
            self.assertEqual(rotator.main(),1)
        self.assertFalse(state.exists())
        self.assertFalse(state.with_name('backup.json').exists())
        self.assertFalse(state.with_name('watcher.pid').exists())

    def test_unknown_session_is_not_alive(self):
        self.assertFalse(rotator.session_alive(None))

    def test_watcher_stops_if_session_exits_or_pid_is_reused(self):
        stat=self.root/'stat'
        stat.write_text(' '.join(['0']*21+['100']))
        session=(stat,'100')
        self.assertTrue(rotator.session_alive(session))
        stat.write_text(' '.join(['0']*21+['200']))
        self.assertFalse(rotator.session_alive(session))
        stat.unlink()
        self.assertFalse(rotator.session_alive(session))

    def test_calendar_selection_repeats_wraps_and_catches_up(self):
        images = rotator.load_manifest(self.manifest)
        for day, name in [(dt.date(2026,10,31),'one space.png'),(dt.date(2026,10,31),'one space.png'),(dt.date(2026,11,1),'two.png'),(dt.date(2026,11,3),'one space.png'),(dt.date(2026,11,8),'three.png')]:
            self.assertEqual(rotator.choose(images,day).name,name)
    def test_manifest_fails_closed(self):
        for data in [[], {}, [{'id':'a','title':'a','file':'../bad.png'}], self.entries+[self.entries[0]], [dict(id='a',title='a',file='missing.png')], [dict(id='a',title='a',file='/etc/passwd')]]:
            self.manifest.write_text(json.dumps(data))
            with self.assertRaises(ValueError): rotator.load_manifest(self.manifest)
        self.manifest.write_text('{broken')
        with self.assertRaises(ValueError): rotator.load_manifest(self.manifest)
    def test_symlink_escape_and_duplicate_file_fail_closed(self):
        with tempfile.TemporaryDirectory() as external:
            target=Path(external)/'outside.png'; target.write_bytes(b'png')
            (self.root/'escape.png').symlink_to(target)
            for entries in [[dict(id='escape',title='escape',file='escape.png')],self.entries+[dict(id='unique',title='duplicate',file='two.png')]]:
                self.manifest.write_text(json.dumps(entries))
                with self.assertRaises(ValueError): rotator.load_manifest(self.manifest)

    def test_xfce_all_properties_exact_args_state_and_refresh(self):
        calls=[]
        props={'/backdrop/screen0/monitor0/workspace0/last-image':'old.png','/backdrop/screen0/monitor1/image-path':'other.png','/backdrop/screen0/monitor0/workspace0/image-style':'3','/unrelated/last-image':'untouched'}
        def run(args, **kw):
            import subprocess
            calls.append(args)
            if args[-1]=='-l': return subprocess.CompletedProcess(args,0,'\n'.join(props),'')
            prop=args[args.index('-p')+1]
            if '-s' in args: props[prop]=args[-1]; return subprocess.CompletedProcess(args,0,'','')
            return subprocess.CompletedProcess(args,0,props[prop]+'\n','')
        state=self.root/'state.json'; chosen=self.root/'one space.png'
        rotator.apply(chosen,state,run)
        self.assertEqual(props['/backdrop/screen0/monitor1/image-path'],str(chosen))
        self.assertEqual(props['/backdrop/screen0/monitor0/workspace0/image-style'],'4')
        self.assertNotIn('/backdrop/screen0/monitor1/image-style',props)
        self.assertEqual(props['/unrelated/last-image'],'untouched')
        self.assertEqual(json.loads(state.read_text())['previous']['/backdrop/screen0/monitor1/image-path'],'other.png')
        self.assertIn(['xfconf-query','-c','xfce4-desktop','-p','/backdrop/screen0/monitor1/image-path','-s',str(chosen)],calls)
        props['/backdrop/screen0/monitor1/image-path']='reset'
        rotator.apply(chosen,state,run)
        self.assertEqual(props['/backdrop/screen0/monitor1/image-path'],str(chosen))
        self.assertEqual(json.loads(state.read_text())['previous']['/backdrop/screen0/monitor1/image-path'],'other.png')
    def test_failed_command_does_not_commit_state(self):
        import subprocess
        def fail(args,**kw):
            if args[-1]=='-l': return subprocess.CompletedProcess(args,0,'/backdrop/screen0/monitor0/last-image','')
            if '-s' in args: raise subprocess.CalledProcessError(1,args)
            return subprocess.CompletedProcess(args,0,'old.png','')
        state=self.root/'state.json'
        with self.assertRaises(subprocess.CalledProcessError): rotator.apply(self.root/'two.png',state,fail)
        self.assertFalse(state.exists())
        self.assertEqual(json.loads((self.root/'backup.json').read_text())['previous']['/backdrop/screen0/monitor0/last-image'],'old.png')

if __name__=='__main__': unittest.main()
