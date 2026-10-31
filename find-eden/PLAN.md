# Find Eden wallpaper game

User request: add a small white, blonde-haired girl playing hide-and-seek to the Eden wallpapers, and use them for a FIND EDEN game.

Implementation: preserve originals; generate three new scenes with the same character clothing and hair. Package original full-resolution wallpaper PNGs plus an offline single-file browser game. Generous click/touch targets, optional text hint and visual reveal, untimed play, no scores or stored progress. Keyboard arrows move a search ring, Enter/Space checks the location. A labelled location-choice alternative supports play without precise pointing. The desktop wallpaper itself remains a static image; clicks work inside the game. Do not change installed OS wallpaper, login or startup configuration.

Steps:
- [x] Generate and visually inspect three edited wallpaper scenes.
- [x] Write failing tests for normalized hit regions, forgiving touch targets, blocked invalid coordinates, and independent scene state.
- [x] Build self-contained game with each corresponding scene, guide, retry, next and replay controls.
- [x] Exercise correct and wrong clicks, hints, keyboard, accessible location choices, scene progression, reset and responsive layout using actual game code and deterministic image fixtures on the server browser. Inspect image dimensions and encoded production asset mapping locally.
- [x] Package game and full-resolution wallpapers, retain the unchanged source activity pack, and save the new deliverable.

Expanded scope completed: 25 additional original scenes, all 28 mapped into the offline game, and a tested per-user daily changer. Native iMac activation remains outstanding; no desktop services were activated on another device.
