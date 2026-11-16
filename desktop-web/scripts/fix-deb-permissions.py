#!/usr/bin/env python3
"""Fix packaging mode of generated desktop entry without changing app contents."""
import os, pathlib, subprocess, sys, tempfile
pkg=pathlib.Path(sys.argv[1]).resolve()
if not pkg.is_file() or pkg.suffix!='.deb':raise SystemExit('Expected existing .deb')
with tempfile.TemporaryDirectory(prefix='eden-deb-') as tmp:
 root=pathlib.Path(tmp)/'package'
 subprocess.run(['dpkg-deb','-R',str(pkg),str(root)],check=True)
 desktop=root/'usr/share/applications/EdensGarden.desktop'
 if not desktop.is_file():raise SystemExit('Missing desktop entry')
 desktop.chmod(0o644)
 (root/'DEBIAN').chmod(0o755)
 for control in (root/'DEBIAN').iterdir():
  if control.is_file():control.chmod(0o755 if control.name in ('postinst','prerm','postrm','preinst') else 0o644)
 # Preserve executable modes; ensure installed directories are traversable.
 for directory in [root,root/'opt',root/'opt/Edens Garden']:
  if directory.is_dir():directory.chmod(0o755)
 output=pkg.with_name(pkg.stem+'.fixed.deb')
 subprocess.run(['dpkg-deb','--build','--root-owner-group',str(root),str(output)],check=True)
 os.replace(output,pkg)
 print('FIXED_DESKTOP_ENTRY_MODE',oct(desktop.stat().st_mode & 0o777))
