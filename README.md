Wallpaper Daemon

A lightweight Python utility that automatically changes your desktop wallpaper from wallpaperscraft.com
 sequentially from the last page to the first. The program runs completely in the background, supports a system tray icon, logs all wallpaper changes, and remembers your current position after reboot.

Features

✅ Automatically changes wallpaper every 6 hours (configurable)

✅ Goes sequentially from page 6919 → 1

✅ Works silently in the background (.pyw for Windows)

✅ System tray icon with menu:

Change Now – immediately sets the next wallpaper

Pause / Resume – pause or resume automatic changes

Exit – stops the daemon

✅ Keeps a log file (wallpaper_log.txt) with all changes

✅ Remembers the current page and wallpaper index after restart (wallpaper_state.json)

Installation

Clone the repository:

git clone https://github.com/walik7496/wallpaper-daemon.git
cd wallpaper-daemon


Install required Python packages:

pip install -r requirements.txt


Requirements:

requests

beautifulsoup4

pystray

pillow

Usage
Run in Background (Windows)

Save the script as:

wallpapers_daemon.pyw


Double-click the file. It will run silently in the system tray.

System Tray Menu

Change Now – set the next wallpaper immediately

Pause / Resume – stop or resume automatic wallpaper changes

Exit – quit the program

Log

All wallpaper changes are recorded in wallpaper_log.txt:

[Sat Nov 9 12:00:00 2025] ✅ Wallpaper from page 6919, index 1: <URL>
[Sat Nov 9 18:00:00 2025] 🖼️ Manual change: page 6919, index 2: <URL>

Persistent State

The program remembers your current page and index in:

wallpaper_state.json


So after a reboot, it resumes from the last wallpaper, not from the first.

Configuration

Change interval: default 6 hours → modify in script:

delay_hours = 6


Start page: default 6919 → modify:

start_page = 6919

How it Works

Fetches wallpapers from wallpaperscraft.com by page

Stores current page and wallpaper index in wallpaper_state.json

Sets wallpaper via Windows API (ctypes)

Runs continuously in a background thread with tray icon controls

Notes

Tested on Windows 10/11

To run automatically at startup, place a shortcut to wallpapers_daemon.pyw in:

shell:startup

Fully background process with system tray icon, logging, and persistent state
