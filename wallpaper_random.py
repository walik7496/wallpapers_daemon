from bs4 import BeautifulSoup
import requests
import time
import ctypes
import os
import threading
from PIL import Image, ImageDraw
import pystray
import json
import random

# ---------------- State ----------------

state_file = "wallpaper_state.json"
seen_file = "seen_wallpapers.json"
start_page = 6919
delay_hours = 6
delay_seconds = delay_hours * 3600

def save_state(page):
    with open(state_file, "w") as f:
        json.dump({"page": page}, f)

def load_state():
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            data = json.load(f)
            return data.get("page", start_page)
    return start_page

def load_seen():
    if os.path.exists(seen_file):
        with open(seen_file, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(seen_file, "w") as f:
        json.dump(list(seen), f)

current_page = load_state()
seen_wallpapers = load_seen()

# ---------------- Wallpaper Actions ----------------

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
    # ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 1 | 2)

# ---------------- Logging ----------------

def log(message):
    with open("wallpaper_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{time.ctime()}] {message}\n")

# ---------------- Loop ----------------

running = True
paused = False

def wallpaper_loop():
    global current_page, running, paused, seen_wallpapers

    while running:
        if paused:
            time.sleep(5)
            continue

        wallpapers = get_wallpapers(current_page)

        if not wallpapers:
            log(f"⚠️ No wallpapers on page {current_page}")
        else:
            # фільтруємо, щоб не повторювати
            possible = [w for w in wallpapers if w not in seen_wallpapers]

            # якщо фото на цій сторінці закінчилися — перехід
            if not possible:
                log(f"📭 Page {current_page} exhausted, switching page...")
                current_page -= 1
                if current_page < 1:
                    current_page = start_page
                save_state(current_page)
                continue

            # вибір рандомної картинки
            url = random.choice(possible)

            seen_wallpapers.add(url)
            save_seen(seen_wallpapers)

            path = download_wallpaper(url)
            set_wallpaper(path)
            log(f"🎲 Random wallpaper set from page {current_page}: {url}")
            save_state(current_page)

            # таймер між змінами
            for _ in range(int(delay_seconds / 10)):
                if not running or paused:
                    break
                time.sleep(10)

        # перехід на попередню сторінку
        current_page -= 1
        if current_page < 1:
            log("🔁 Restarting page cycle!")
            current_page = start_page

        save_state(current_page)


# ---------------- Tray System ----------------

def change_now():
    global current_page, seen_wallpapers

    wallpapers = get_wallpapers(current_page)
    if not wallpapers:
        log("⚠️ No wallpapers for manual change.")
        return

    possible = [w for w in wallpapers if w not in seen_wallpapers]
    if not possible:
        log("📭 Page fully seen. Switching...")
        current_page -= 1
        if current_page < 1:
            current_page = start_page
        save_state(current_page)
        return change_now()

    url = random.choice(possible)
    seen_wallpapers.add(url)
    save_seen(seen_wallpapers)

    path = download_wallpaper(url)
    set_wallpaper(path)

    log(f"🖼️ Manual random change: {url}")
    save_state(current_page)


def reset_history(icon, item):
    global seen_wallpapers
    seen_wallpapers.clear()
    save_seen(seen_wallpapers)
    log("♻️ Wallpaper history reset")


def on_change_now(icon, item):
    global paused
    paused = False
    threading.Thread(target=change_now, daemon=True).start()


def on_pause_resume(icon, item):
    global paused
    paused = not paused
    log("⏸ Paused" if paused else "▶️ Resumed")


def on_exit(icon, item):
    global running
    running = False
    icon.stop()
    log("❌ Program Exited")


def create_image():
    img = Image.new('RGB', (64, 64), color='blue')
    d = ImageDraw.Draw(img)
    d.rectangle((8, 8, 56, 56), fill='white')
    d.text((18, 20), "W", fill='black')
    return img


def setup_tray():
    icon = pystray.Icon(
        "Wallpaper Randomizer",
        create_image(),
        "Wallpaper Randomizer",
        menu=pystray.Menu(
            pystray.MenuItem("Change Now", on_change_now),
            pystray.MenuItem("Pause / Resume", on_pause_resume),
            pystray.MenuItem("Reset History", reset_history),
            pystray.MenuItem("Exit", on_exit)
        )
    )

    threading.Thread(target=wallpaper_loop, daemon=True).start()
    icon.run()


if __name__ == "__main__":
    setup_tray()
