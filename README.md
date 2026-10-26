# Desktop Buddy 🍥

A free, open-source Windows desktop companion prototype built with Python and PySide6.

The first version focuses on playful desktop interactions and break reminders:
- Configurable focus interval (default: 30 minutes)
- Break countdown (default: 5 minutes)
- Full-screen animated shadow-clone-style overlay
- Sound toggle using built-in system sounds
- Dismiss with **Escape**, or snooze for five minutes
- Pause/resume and a tray menu
- No AI API, network access, or paid subscription required

> **Artwork note:** The starter draws placeholder ninja-like characters with Qt shapes. Add only artwork and sounds whose licences permit your intended use. Naruto and related characters are copyrighted; for a distributable open-source release, use original, appropriately licensed character assets.

## Requirements

- Windows 10/11
- Python 3.10+ (3.11 or 3.12 recommended)

## Run from source

Open PowerShell in the repository folder:

```powershell
py -m pip install -r requirements.txt
py main.py
```

If the Python launcher is unavailable, use `python` instead of `py`.

## Controls

- **Start / Apply settings** — apply the interval and break duration; reset the focus timer.
- **Pause timer** — pause or resume the focus countdown.
- **Test Shadow Clone Jutsu now** — preview the break overlay immediately.
- **Escape** — dismiss the overlay.
- **Dismiss** — end the current break overlay.
- **Snooze +5 min** — close the overlay and remind again in five minutes.
- **Exit Naruto Buddy** — close the application safely.
- **System tray** — show settings, test the overlay, or exit.

The full-screen overlay is visual only. It does not lock the computer or disable Windows shortcuts. Keep the app running for reminders to work; this prototype does not yet start automatically with Windows.

## Project status

Early prototype. The timer and interactive overlay are the first milestone. Future contributions can add proper sprite-sheet animation, a draggable transparent desktop character, local notes, sound assets, and mini-games.

## Contributing

Issues and pull requests are welcome. Before contributing artwork, animations, fonts, or audio, make sure the licence allows redistribution and document it in `ASSET-LICENSES.md`.

## Licence

The source code is released under the MIT License. This licence does not automatically apply to third-party art, sound, or other assets included separately.
