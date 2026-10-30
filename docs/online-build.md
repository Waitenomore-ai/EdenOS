# Build Eden OS online

The GitHub Actions workflow builds a development ISO on a temporary Ubuntu
runner using a privileged Debian 13 container. It runs manually, needs no API
keys, has read-only repository permission, and does not publish a release.
The first remote build has not been run yet.

1. Create a GitHub repository named `eden-os`. Private keeps development source
   private; build minutes and artifact storage are subject to your account's
   allowances. Check billing before running if you have enabled paid usage.
2. Extract the source ZIP. Upload the CONTENTS of the `eden-os` folder at the
   repository root, including `.github/workflows/build-iso.yml`. Uploading the
   ZIP alone will not install the workflow. If your file picker hides `.github`,
   create `.github/workflows/build-iso.yml` using GitHub's Add file editor and
   paste in the supplied workflow.
3. Commit to the default branch. Open Actions, select Build Eden OS ISO, and
   choose Run workflow on the default branch.
4. After success, download the `eden-os-test-iso-N` artifact and extract it.
   This contains the ISO, checksum, and build information. Artifacts expire
   after seven days; download them promptly. Failed builds retain their log
   if the build reached the logging step.
5. On Windows, use `Get-FileHash .\eden-os-amd64-test.iso -Algorithm SHA256`
   and compare the result with the checksum file.
6. Boot-test the ISO on a disposable VM or a spare computer using Ventoy.
   Building online does not verify child controls, browser filtering,
   accessibility, installation, recovery, or hardware compatibility.

The workflow uses GitHub's checkout and artifact actions v6 and Debian's
`trixie` container tag. These version tags and package archives can change;
this is an automated source build, not a byte-for-byte reproducible build.
