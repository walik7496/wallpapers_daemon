from bs4 import BeautifulSoup
import requests
import time
import ctypes
import os
import threading
from PIL import Image, ImageDraw
import pystray
import json

# ---------------- State Management ----------------
state_file = "wallpaper_state.json"

def save_state(page, index):
    with open(state_file, "w") as f:
        json.dump({"page": page, "index": index}, f)

def load_state():
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            data = json.load(f)
            return data.get("page", 6919), data.get("index", 0)
    return 6919, 0

current_page, current_index = load_state()

# ---------------- Wallpaper Functions ----------------
def get_wallpapers(page=1):
    url = f"https://wallpaperscraft.com/all/page{page}"
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser")

    wallpapers = []
    for i in html.find_all("img", {"class": "wallpapers__image"}):
        wallpapers.append(i['src'].replace("300x168", "1920x1080"))
    return wallpapers

def download_wallpaper(url):
    path = os.path.join(os.getcwd(), "wallpaper.jpg")
    response = requests.get(url)
    with open(path, "wb") as f:
        f.write(response.content)
    return path

def set_wallpaper(path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

# ---------------- Logging ----------------
def log(message):
    with open("wallpaper_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{time.ctime()}] {message}\n")

# ---------------- Wallpaper Loop ----------------
running = True
paused = False
delay_hours = 6
delay_seconds = delay_hours * 3600
start_page = 6919

def wallpaper_loop():
    global current_page, current_index, running, paused
    page = current_page

    while running:
        if paused:
            time.sleep(5)
            continue

        wallpapers = get_wallpapers(page)
        if not wallpapers:
            log(f"⚠️ No wallpapers on page {page}")
        else:
            for idx in range(current_index, len(wallpapers)):
                if not running or paused:
                    break
                url = wallpapers[idx]
                path = download_wallpaper(url)
                set_wallpaper(path)
                log(f"✅ Wallpaper from page {page}, index {idx + 1}: {url}")

                # Update state
                current_page, current_index = page, idx + 1
                if current_index >= len(wallpapers):
                    current_index = 0
                    page = page - 1 if page > 1 else start_page
                    current_page = page
                save_state(current_page, current_index)

                # Wait 6 hours
                for _ in range(int(delay_seconds/10)):
                    if not running or paused:
                        break
                    time.sleep(10)

        page -= 1
        if page < 1:
            log(f"🔁 Reached page 1, restarting from {start_page}")
            page = start_page
            current_page = page
            current_index = 0
            save_state(current_page, current_index)

# ---------------- Tray Icon ----------------
def create_image():
    img = Image.new('RGB', (64, 64), color='blue')
    d = ImageDraw.Draw(img)
    d.rectangle((8, 8, 56, 56), fill='white')
    d.text((18, 20), "W", fill='black')
    return img

def change_now():
    global current_page, current_index
    wallpapers = get_wallpapers(current_page)
    if not wallpapers:
        log("⚠️ No wallpapers for manual change.")
        return

    url = wallpapers[current_index % len(wallpapers)]
    path = download_wallpaper(url)
    set_wallpaper(path)
    log(f"🖼️ Manual change: page {current_page}, index {current_index + 1}: {url}")

    current_index += 1
    if current_index >= len(wallpapers):
        current_index = 0
        current_page -= 1
        if current_page < 1:
            current_page = start_page
    save_state(current_page, current_index)

def on_change_now(icon, item):
    global paused
    paused = False
    threading.Thread(target=change_now, daemon=True).start()

def on_pause_resume(icon, item):
    global paused
    paused = not paused
    state = "⏸ Paused" if paused else "▶️ Resumed"
    log(state)

def on_exit(icon, item):
    global running
    running = False
    icon.stop()
    log("❌ Exited program")

def setup_tray():
    image = create_image()
    menu = pystray.Menu(
        pystray.MenuItem("Change Now", on_change_now),
        pystray.MenuItem("Pause / Resume", on_pause_resume),
        pystray.MenuItem("Exit", on_exit)
    )
    icon = pystray.Icon("Wallpaper Daemon", image, "Wallpaper Daemon", menu)
    threading.Thread(target=wallpaper_loop, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    setup_tray()
