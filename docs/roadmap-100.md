# EdenOS 100-item execution tracker

User-approved scope, 30 October 2026. Source implementation is separate from
ISO verification and physical-device verification. No item is marked verified
from code inspection alone. Current baseline before this batch: e272020.

Status: **Source** = implemented, needs image/device check; **Blocked** = needs
physical device or runtime evidence; **Pending** = not yet implemented/tested.

| # | Task | Status / evidence needed |
|---|---|---|
1|Identify current USB version|Blocked: iMac/USB access|
2|Record exact Intel iMac model|Blocked: run eden-system-report on iMac|
3|Diagnose wrong boot device|Blocked: firmware/media evidence|
4|Inspect USB boot files and partitions|Blocked: USB read access|
5|Identify iMac EFI width|Blocked: system report includes firmware_bits|
6|Verify required EFI loader in ISO|Pending: inspect built ISO|
7|Verify legacy BIOS boot|Pending: diagnostic available, visual boot required|
8|Separate UEFI diagnostic|Source: boot-smoke uefi, disposable OVMF vars; tests pass|
9|Record boot results with ISO|Pending: real boot evidence|
10|Identify Eden boot menu|Pending|
11|Clearly label live session|Pending|
12|Clearly label installer|Pending|
13|Verify installed Eden configuration|Blocked: disposable installation|
14|Verify installed bootloader|Blocked: disposable installation|
15|Show target disk model/capacity|Pending|
16|Confirm before target erasure|Pending: installer review; no automatic disk writes added|
17|Test disposable VM installation|Blocked: VM runtime|
18|Boot installed system without USB|Blocked: VM/device|
19|Verified iMac installation procedure|Blocked: successful iMac installation evidence|
20|New ISO with latest fixes|Pending: online build|
21|Resolve repository artwork files|Source: approved pack assets included|
22|Include approved Eden logo|Source: existing staging validates and copies it|
23|Include all six wallpapers|Source: all six named PNGs validated|
24|Verify artwork inside ISO|Pending: existing workflow has image inspection gate|
25|Check login appearance|Blocked: real graphical session|
26|Check adult desktop wallpaper|Blocked: real graphical session|
27|Check child launcher branding|Blocked: real graphical session|
28|Remove stale version/build instructions|Source: current addendum in online-build.md|
29|Show installed version in adult settings|Partial: build identity shown in adult-help screen|
30|Show build date/source commit|Source: build.json writer and help label, tests pass|
31|Verify installer adult account creation|Blocked: disposable installation|
32|Verify child has no admin privileges|Blocked: account runtime audit|
33|Test child creation via PolicyKit|Blocked: Debian system bus/session|
34|Test cancelled adult authentication|Blocked: Debian PolicyKit session|
35|Test partial account cleanup|Blocked: disposable account runtime|
36|Helpful existing-username message|Pending|
37|Prevent duplicate setup submissions|Source existed: create button disabled; runtime check pending|
38|Default child Eden session|Source existed: SetXSession; runtime check pending|
39|Retain adult desktop|Blocked: login/session test|
40|Child return to sign-in|Blocked: login/session test|
41|Audit child keyboard shortcuts|Blocked: real child session|
42|Audit alternate desktop selection|Blocked: LightDM session audit|
43|Audit dialog escape routes|Blocked: real activities/session|
44|Audit terminal/file manager routes|Blocked: real session|
45|Document child-session limitations|Source: release-evidence.md|
46|Verify child shutdown|Blocked: disposable session|
47|Handle blocked shutdown without UI freeze|Pending|
48|Test shutdown with unsaved activity|Blocked: real activity/session|
49|Verify restart/sign-out|Blocked: installed session|
50|Recover from launcher crash|Pending|
51|Home fits smaller screens|Source: wrapping category FlowBox; visual check pending|
52|Footer fits larger text|Source: wrapping FlowBox; visual check pending|
53|All screens at maximum text scaling|Partial: opt-in GTK smoke; allocation/visual checks pending|
54|Predictable focus after navigation|Pending|
55|Visible keyboard focus|Source: explicit button/high-contrast focus styles; visual check pending|
56|Useful screen-reader labels|Blocked: actual assistive-technology test|
57|Screen-reader test|Blocked: desktop/screen reader|
58|Check high contrast throughout|Partial: ordinary buttons now explicit; visual audit pending|
59|Reduced-motion behaviour|Source existed: no automatic animations; runtime audit pending|
60|Touch targets and scrolling|Blocked: supported touch device|
61|Adult setup fits small displays|Source: scroll container; visual check pending|
62|Improve first-profile instructions|Pending|
63|Explain offline features|Source: home-screen explanation|
64|Label internet activities|Source: KidsTube labelled online; browser disabled pending review|
65|Helpful unavailable-activity messages|Source existed; runtime check pending|
66|Prevent duplicate activity windows|Pending|
67|Activity returns to Eden|Blocked: real activity/session|
68|Tux Paint save/reopen|Blocked: real activity session|
69|Correct ownership of saved work|Blocked: disposable child accounts|
70|Child account file isolation|Blocked: account permissions audit|
71|Review GCompris inclusion|Pending: package/licence/offline/accessibility review|
72|Review offline reading activity|Pending|
73|Review offline numeracy activity|Pending|
74|Review offline problem solving|Pending|
75|Review offline typing activity|Pending|
76|Activity licences/attribution|Partial: Tux Paint notes existed; new candidates not reviewed|
77|Activity storage measurement|Blocked: installed activity pack|
78|Offline activity verification|Blocked: disconnected real session|
79|Only reviewed catalogue activities|Source existed; catalogue validation tests pass|
80|Helpful empty categories|Source existed; visual check pending|
81|Resolve browser default conflict|Source: disabled default and shared reviewed-config gate; tests pass|
82|Verify current KidsTube behaviour|Blocked: service/runtime suitability review|
83|Verify actual Firefox policy load|Blocked: target Firefox runtime|
84|Test direct Firefox launch|Blocked: target desktop/runtime|
85|Test URLs outside allowlist|Blocked: target Firefox runtime|
86|Test redirects/pop-ups/windows|Blocked: target Firefox runtime|
87|Test downloads/opened files|Blocked: disposable browser session|
88|Assess embed exceptions|Pending: documented broad exceptions remain unverified|
89|Verify browser data clearing|Blocked: target Firefox runtime|
90|Browser depends on verified adult configuration|Partial: Eden wrapper/button gate implemented; direct OS launch remains open audit|
91|Measure idle memory on 4 GB|Blocked: actual target or representative VM|
92|Measure activity memory|Blocked: running activity|
93|Measure true 32 GB installation|Blocked: representative installed filesystem|
94|Verify 6 GiB free after installation|Blocked: report provides conservative root-only budget check|
95|Nearly-full storage behaviour|Partial: preference failure regression fixed; activity/install checks pending|
96|Adult security-update procedure|Source: maintenance-and-recovery.md; interrupted-update test pending|
97|Interrupted update test|Blocked: disposable installed system|
98|Adult backup/restore procedure|Source: maintenance-and-recovery.md; restore rehearsal pending|
99|Complete end-to-end release test|Blocked: installed system/hardware evidence|
100|Publish tested release/evidence|Blocked: release-evidence.md lists unmet gates|

## Current blockers

- Connected devices are Chris_PC and dripvid; neither is the Intel iMac.
- No permission to erase a disk is inferred from this roadmap. Any eventual
  installation must identify and confirm the selected target at that time.
- The image build can be run online, but real child/session/PolicyKit/accessibility
  and hardware results cannot be inferred from a successful build.
