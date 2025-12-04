import requests
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
from datetime import datetime
import threading
import time
import os
import sys
import argparse
import json

init(autoreset=True)
print_lock = threading.Lock()

checked = 0
valid_count = 0
start_time = None
webhook_url = ""  # Replace with your actual webhook URL

def set_terminal_title(title):
    if os.name == 'nt':
        safe_title = title.replace(":", "-").replace("|", "-")
        os.system(f"title {safe_title}")
    else:
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()

def send_webhook(webhook_url, username):
    try:
        payload = {
            "content": f"✅ **Valid Username Found:** `{username}`"
        }
        headers = {"Content-Type": "application/json"}
        requests.post(webhook_url, data=json.dumps(payload), headers=headers, timeout=5)
    except Exception as e:
        with print_lock:
            print(Fore.YELLOW + f"[ERROR] Webhook failed: {e}")

def log_result(status, username):
    status_label = f"[{status}]".ljust(7)
    username_field = username.ljust(10)
    with print_lock:
        if status == "VALID":
            print(Fore.GREEN + f"{status_label} {username_field}")
        else:
            print(Fore.RED + f"{status_label} {username_field}")

def check_username(username):
    url = f"https://auth.roblox.com/v1/usernames/validate?Username={username}&Birthday=2000-01-01"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "").strip().lower()
            return username, (message == "username is valid")
    except Exception as e:
        with print_lock:
            print(Fore.YELLOW + f"[ERROR] {username} - {e}")
    return username, False

def process_username(username):
    global checked, valid_count
    username, is_valid = check_username(username)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with print_lock:
        checked += 1
        if is_valid:
            valid_count += 1
        elapsed = max(time.time() - start_time, 1)
        cpm = int((checked / elapsed) * 60)
        set_terminal_title(f"RoSnipe: {checked} | Valid: {valid_count} | CPM: {cpm}")

    if is_valid:
        log_result("VALID", username)
        with open("valid.txt", "a") as vf:
            vf.write(f"[{timestamp}] {username}\n")
        send_webhook(webhook_url, username)
    else:
        log_result("TAKEN", username)
        with open("invalid.txt", "a") as inf:
            inf.write(f"[{timestamp}] {username}\n")

def animate_gradient_logo(logo_text, colors, max_width=80, duration=2, delay=0.05):
    """print logo"""
    lines = logo_text.strip('\n').split('\n')
    num_lines = len(lines)
    color_offset = 0
    end_time = time.time() + duration

    print('\n' * num_lines)

    while time.time() < end_time:
        sys.stdout.write(f"\x1b[{num_lines}A")
        for line in lines:
            gradient_line = ""
            for i, char in enumerate(line.rstrip()):
                pos = (i + color_offset) % max_width
                segment_width = max_width / (len(colors) - 1)
                color_index = int(pos / segment_width)
                
                r1, g1, b1 = colors[color_index]
                r2, g2, b2 = colors[color_index + 1]
                
                segment_pos = pos % segment_width
                factor = segment_pos / segment_width
                r, g, b = int(r1 + (r2 - r1) * factor), int(g1 + (g2 - g1) * factor), int(b1 + (b2 - b1) * factor)
                
                gradient_line += f"\x1b[38;2;{r};{g};{b}m{char}"
            print(gradient_line + '\x1b[K')
        color_offset += 1
        time.sleep(delay)

def main():
    global start_time

    logo = r"""
        ___         ___               ___                               ___
        `MM      68b MM      68b      `MM 68b                       68b `MM
         MM      Y89 MM      Y89       MM Y89         /             Y89  MM           /
  ____   MM   __ ___ MM____  ___   ____MM ___        /M      _____  ___  MM   ____   /M
 6MMMMb\ MM   d' `MM MMMMMMb `MM  6MMMMMM `MM       /MMMMM  6MMMMMb `MM  MM  6MMMMb /MMMMM
MM'    ` MM  d'   MM MM'  `Mb MM 6M'  `MM  MM        MM    6M'   `Mb MM  MM 6M'  `Mb MM
YM.      MM d'    MM MM    MM MM MM    MM MM        MM    MM     MM MM  MM MM    MM MM
 YMMMMb  MMdM.    MM MM    MM MM MM    MM MM        MM    MM     MM MM  MM MMMMMMMM MM
     `Mb MMPYM.   MM MM    MM MM MM    MM MM        MM    MM     MM MM  MM MM       MM
L    ,MM MM  YM.  MM MM.  ,M9 MM YM.  ,MM  MM        YM.  ,YM.   ,M9 MM  MM YM    d9 YM.  ,
MYMMMM9 _MM_  YM._MM_MYMMMM9 _MM_ YMMMMMM__MM_        YMMM9 YMMMMM9 _MM__MM_ YMMMM9   YMMM9
"""
    # Define la paleta de colores: Rojo, Negro, Gris, Blanco
    color_palette = [
        (255, 0, 0),    # Rojo
        (0, 0, 0),      # Negro
        (128, 128, 128),# Gris
        (255, 255, 255) # Blanco
    ]
    animate_gradient_logo(logo, color_palette, max_width=80)
    print(Style.RESET_ALL)

    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=20, help="Number of threads (default 20)")
    args = parser.parse_args()

    start_choice = input("Start sniping now? (y/n): ").strip().lower()
    if start_choice != 'y':
        print("Exiting.")
        return

    open("valid.txt", "w").close()
    open("invalid.txt", "w").close()

    with open("usernames.txt", "r") as f:
        usernames = [line.strip() for line in f if line.strip()]

    max_threads = min(len(usernames), args.threads)
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(process_username, usernames)

    elapsed = round(time.time() - start_time, 2)
    print(Fore.CYAN + "\nSummary:")
    print(Fore.CYAN + f"Checked: {checked}")
    print(Fore.GREEN + f"Valid: {valid_count}")
    print(Fore.RED + f"Taken: {checked - valid_count}")
    print(Fore.CYAN + f"Time Elapsed: {elapsed} seconds")

if __name__ == "__main__":
    main()
