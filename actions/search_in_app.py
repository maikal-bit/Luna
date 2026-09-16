"""
actions/search_in_app.py — Direct in-app desktop searching for Luna Assistant.

Searches directly inside installed desktop applications (YouTube Desktop, Spotify,
Discord, Telegram, WhatsApp, File Explorer, Steam, etc.) without falling back to a web browser.
"""

from __future__ import annotations

import os
import sys
import time
import shutil
import platform
import subprocess
from pathlib import Path
from urllib.parse import quote

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.05
    _PYAUTOGUI = True
except ImportError:
    _PYAUTOGUI = False

try:
    import pyperclip
    _PYPERCLIP = True
except ImportError:
    _PYPERCLIP = False

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

_SYSTEM = platform.system()  # "Windows" | "Darwin" | "Linux"

if _SYSTEM == "Windows":
    _WIN_HIDE: dict = {"creationflags": subprocess.CREATE_NO_WINDOW}
else:
    _WIN_HIDE: dict = {}


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def _paste_text(text: str) -> None:
    """Safely pastes text using clipboard + Ctrl+V (or Command+V on macOS)."""
    if not _PYAUTOGUI:
        return
    paste_hotkey = ("command", "v") if _SYSTEM == "Darwin" else ("ctrl", "v")
    if _PYPERCLIP:
        try:
            pyperclip.copy(text)
            time.sleep(0.1)
            pyautogui.hotkey(*paste_hotkey)
            time.sleep(0.1)
            return
        except Exception:
            pass
    pyautogui.write(text, interval=0.03)


def _focus_window_windows(title_query: str) -> bool:
    """Attempts to bring a window matching title_query to the front on Windows."""
    try:
        # 1. Try WScript.Shell AppActivate (fast and reliable)
        ps_cmd = f'(New-Object -ComObject WScript.Shell).AppActivate("{title_query}")'
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=4, **_WIN_HIDE
        )
        if "True" in result.stdout:
            time.sleep(0.2)
            return True
    except Exception:
        pass

    return False


def _find_start_menu_shortcut(query: str) -> str | None:
    """Searches Windows Start Menu for matching .lnk shortcuts."""
    if _SYSTEM != "Windows":
        return None

    clean_q = query.lower().strip()
    appdata = Path(os.environ.get("APPDATA", ""))
    programdata = Path(os.environ.get("PROGRAMDATA", ""))
    start_dirs = [
        appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        programdata / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    ]

    candidates = []
    for sdir in start_dirs:
        if not sdir.exists():
            continue
        for lnk in sdir.rglob("*.lnk"):
            stem = lnk.stem.lower()
            if stem == clean_q:
                return str(lnk)
            if clean_q in stem or stem in clean_q:
                candidates.append((len(stem), str(lnk)))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    return None


def _find_youtube_desktop_binary() -> str | None:
    """Finds the installed YouTube Desktop app on Windows."""
    if _SYSTEM != "Windows":
        return None

    # Check direct installation paths
    userprofile = Path(os.environ.get("USERPROFILE", ""))
    localappdata = Path(os.environ.get("LOCALAPPDATA", ""))
    programfiles = Path(os.environ.get("PROGRAMFILES", ""))
    programfiles_x86 = Path(os.environ.get("PROGRAMFILES(X86)", ""))

    known_paths = [
        userprofile / "YouTube Desktop" / "ytdesktop.exe",
        localappdata / "Programs" / "YouTube Desktop" / "ytdesktop.exe",
        localappdata / "YouTube Desktop" / "ytdesktop.exe",
        programfiles / "YouTube Desktop" / "ytdesktop.exe",
        programfiles_x86 / "YouTube Desktop" / "ytdesktop.exe",
    ]
    for kp in known_paths:
        if kp.exists():
            return str(kp)

    # Check Start Menu shortcut
    lnk = _find_start_menu_shortcut("YouTube Desktop")
    if lnk:
        return lnk

    return None


def _is_process_running(name_pattern: str) -> bool:
    """Checks if a process matching name_pattern is currently running."""
    if not _PSUTIL:
        return False
    pattern = name_pattern.lower()
    for p in psutil.process_iter(["name"]):
        try:
            if pattern in p.info["name"].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def _launch_desktop_target(target: str) -> bool:
    """Launches an executable, .lnk shortcut, or URI."""
    try:
        if _SYSTEM == "Windows":
            if hasattr(os, "startfile") and (os.path.exists(target) or ":" in target):
                os.startfile(target)
                return True
            subprocess.Popen(f'start "" "{target}"', shell=True, **_WIN_HIDE)
            return True
        elif _SYSTEM == "Darwin":
            subprocess.Popen(["open", target])
            return True
        else:
            subprocess.Popen(["xdg-open", target])
            return True
    except Exception as e:
        print(f"[search_in_app] Failed to launch {target}: {e}")
        return False


def _search_youtube(query: str, play_first: bool = False) -> str:
    """Performs search directly inside the YouTube Desktop application."""
    yt_binary = _find_youtube_desktop_binary()
    is_running = _is_process_running("ytdesktop")

    if yt_binary:
        print(f"[search_in_app] Using YouTube Desktop binary/shortcut: {yt_binary}")
        if is_running:
            _focus_window_windows("YouTube")
            time.sleep(0.3)
        else:
            _launch_desktop_target(yt_binary)
            time.sleep(2.5)
            _focus_window_windows("YouTube")
    else:
        # If no desktop app found, use Start Menu / open_app
        from actions.open_app import open_app as _open_app_fn
        _open_app_fn(parameters={"app_name": "youtube"})
        time.sleep(2.0)
        _focus_window_windows("YouTube")

    # In YouTube (desktop app or web view), '/' jumps straight to the search box!
    if _PYAUTOGUI:
        time.sleep(0.3)
        # Press '/' to focus search input
        pyautogui.press("/")
        time.sleep(0.2)
        # Select all and delete any existing query
        select_all = ("command", "a") if _SYSTEM == "Darwin" else ("ctrl", "a")
        pyautogui.hotkey(*select_all)
        time.sleep(0.05)
        pyautogui.press("backspace")
        time.sleep(0.05)
        # Paste new search query and submit
        _paste_text(query)
        time.sleep(0.15)
        pyautogui.press("enter")

        if play_first:
            time.sleep(2.5)
            # Press enter or tab+enter on the first result
            pyautogui.press("tab")
            time.sleep(0.1)
            pyautogui.press("enter")

    return f"Searched for '{query}' directly inside YouTube Desktop."


def _search_spotify(query: str, play_first: bool = False) -> str:
    """Performs search directly inside Spotify desktop application."""
    # Spotify has native deep-link search support: spotify:search:<query>
    uri = f"spotify:search:{quote(query)}"
    print(f"[search_in_app] Opening Spotify URI: {uri}")
    _launch_desktop_target(uri)
    time.sleep(1.0)
    _focus_window_windows("Spotify")

    if play_first and _PYAUTOGUI:
        time.sleep(1.5)
        pyautogui.press("enter")

    return f"Searched for '{query}' directly inside Spotify."


def _search_discord(query: str) -> str:
    """Performs search directly inside Discord."""
    is_running = _is_process_running("discord")
    if is_running:
        _focus_window_windows("Discord")
        time.sleep(0.3)
    else:
        discord_lnk = _find_start_menu_shortcut("Discord")
        if discord_lnk:
            _launch_desktop_target(discord_lnk)
        else:
            _launch_desktop_target("discord:")
        time.sleep(2.5)
        _focus_window_windows("Discord")

    if _PYAUTOGUI:
        time.sleep(0.4)
        # Ctrl+K opens quick switcher / search
        pyautogui.hotkey("ctrl", "k")
        time.sleep(0.2)
        select_all = ("command", "a") if _SYSTEM == "Darwin" else ("ctrl", "a")
        pyautogui.hotkey(*select_all)
        time.sleep(0.05)
        pyautogui.press("backspace")
        _paste_text(query)
        time.sleep(0.2)
        pyautogui.press("enter")

    return f"Searched for '{query}' directly inside Discord."


def _search_telegram(query: str) -> str:
    """Performs search directly inside Telegram Desktop."""
    is_running = _is_process_running("telegram")
    if is_running:
        _focus_window_windows("Telegram")
        time.sleep(0.3)
    else:
        tele_lnk = _find_start_menu_shortcut("Telegram")
        if tele_lnk:
            _launch_desktop_target(tele_lnk)
        else:
            _launch_desktop_target("tg:")
        time.sleep(2.0)
        _focus_window_windows("Telegram")

    if _PYAUTOGUI:
        time.sleep(0.3)
        # Ctrl+F focuses search in Telegram
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.2)
        select_all = ("command", "a") if _SYSTEM == "Darwin" else ("ctrl", "a")
        pyautogui.hotkey(*select_all)
        time.sleep(0.05)
        pyautogui.press("backspace")
        _paste_text(query)
        time.sleep(0.15)
        pyautogui.press("enter")

    return f"Searched for '{query}' directly inside Telegram."


def _search_whatsapp(query: str) -> str:
    """Performs search directly inside WhatsApp Desktop."""
    is_running = _is_process_running("whatsapp")
    if is_running:
        _focus_window_windows("WhatsApp")
        time.sleep(0.3)
    else:
        wa_lnk = _find_start_menu_shortcut("WhatsApp")
        if wa_lnk:
            _launch_desktop_target(wa_lnk)
        else:
            _launch_desktop_target("whatsapp:")
        time.sleep(2.0)
        _focus_window_windows("WhatsApp")

    if _PYAUTOGUI:
        time.sleep(0.3)
        # Ctrl+F focuses search in WhatsApp
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.2)
        _paste_text(query)
        time.sleep(0.15)
        pyautogui.press("enter")

    return f"Searched for '{query}' directly inside WhatsApp."


def _search_explorer(query: str) -> str:
    """Performs search directly inside Windows File Explorer."""
    _launch_desktop_target("explorer.exe")
    time.sleep(1.0)
    _focus_window_windows("File Explorer")

    if _PYAUTOGUI:
        time.sleep(0.3)
        # Ctrl+E or F3 focuses search bar in File Explorer
        pyautogui.hotkey("ctrl", "e")
        time.sleep(0.2)
        _paste_text(query)
        time.sleep(0.15)
        pyautogui.press("enter")

    return f"Searched for '{query}' in File Explorer."


def _search_generic(app_name: str, query: str) -> str:
    """Generic fallback for searching inside any desktop app using Ctrl+F or /."""
    from actions.open_app import open_app as _open_app_fn
    _open_app_fn(parameters={"app_name": app_name})
    time.sleep(1.5)
    _focus_window_windows(app_name)

    if _PYAUTOGUI:
        time.sleep(0.3)
        # Universal search shortcut in desktop apps
        search_key = ("command", "f") if _SYSTEM == "Darwin" else ("ctrl", "f")
        pyautogui.hotkey(*search_key)
        time.sleep(0.2)
        _paste_text(query)
        time.sleep(0.15)
        pyautogui.press("enter")

    return f"Searched for '{query}' inside {app_name}."


def search_in_app(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    params = parameters or {}
    app_raw = params.get("app_name", "").strip().lower()
    query = params.get("query", "").strip()
    play_first = bool(params.get("play_first", False))

    if not app_raw:
        return "Please specify which application you would like to search in."
    if not query:
        return f"Please specify what you would like to search for inside {app_raw}."

    if player:
        player.write_log(f"[search_in_app] {app_raw}: '{query}'")
    print(f"[search_in_app] App: '{app_raw}'  Query: '{query}'  PlayFirst: {play_first}")

    # Route to app-specific native handler
    if any(k in app_raw for k in ["youtube", "ytdesktop"]):
        return _search_youtube(query, play_first=play_first)

    if "spotify" in app_raw:
        return _search_spotify(query, play_first=play_first)

    if "discord" in app_raw:
        return _search_discord(query)

    if "telegram" in app_raw:
        return _search_telegram(query)

    if "whatsapp" in app_raw:
        return _search_whatsapp(query)

    if any(k in app_raw for k in ["explorer", "file", "folder", "files"]):
        return _search_explorer(query)

    return _search_generic(app_raw, query)


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "search_in_app",
    "description": (
        "Searches directly inside an installed desktop application (e.g. YouTube, Spotify, "
        "Discord, Telegram, WhatsApp, File Explorer, Steam, etc.). Use this WHENEVER the user "
        "asks to search inside an app (e.g. 'search for lofi on YouTube', 'search in YouTube for rock music', "
        "'search for artist in Spotify', 'search in Discord', 'search for file in Explorer'). "
        "NEVER search in a web browser or use web_search when the user asks to search inside an application."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "app_name": {
                "type": "STRING",
                "description": "Name of the application to search inside (e.g. 'YouTube', 'Spotify', 'Discord', 'Telegram', 'File Explorer')"
            },
            "query": {
                "type": "STRING",
                "description": "The search query or keyword to type into the application"
            },
            "play_first": {
                "type": "BOOLEAN",
                "description": "Whether to automatically play or select the first result (e.g. For music or videos)"
            }
        },
        "required": [
            "app_name",
            "query"
        ]
    },
    "handler": search_in_app,
}
