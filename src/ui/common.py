"""Imports y constantes compartidos por los modulos de la UI."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import subprocess
import shutil
import time
import webbrowser
import copy
import sys
import tempfile
import threading
import glob
from datetime import datetime

from logic.cheats import (
    max_kings, max_quantity, max_skill, set_rarity, set_platinum,
    SOCKET_UPGRADES, get_duplicate_id_map, LEGEND_SKILLS,
    ORANGE_CRAFTPLANS, WEAPON_NAMES, COLLECTIBLES
)
from logic.plugin_loader import load_plugins
from logic.updater import check_updates_async
from logic.config import load_config, save_config, create_save_backup, list_save_backups, atomic_replace, prune_backups
from logic.save_service import SaveService, SaveError
from logic.version import CURRENT_VERSION
from logic.item_names import (
    ITEM_DICTIONARY, ADD_ITEM_PRESETS,
    get_display_name, get_socket_display_name, get_craftplan_display_name,
    AMMO_DEFINITIONS, get_ammo_data, set_ammo_value, max_all_ammo
)
from ui.theme import (
    apply_dark_theme, BG_MAIN, BG_SECONDARY, BG_CARD, BG_INPUT,
    FG_MAIN, FG_MUTED, ACCENT_ORANGE, ACCENT_BLUE, SELECTION_BG,
    BORDER_COLOR, RARITY_COLORS
)

EDITOR_DIR = r"C:\Editor"
DEFAULT_JSON = os.path.join(EDITOR_DIR, "save_coop_0.sav(edited).json")
SAVE_PATH = os.path.join(EDITOR_DIR, "save_coop_0.sav")

# Carpetas y archivos temporales seguros
TEMP_DIR = os.path.join(tempfile.gettempdir(), "dying_light_save_editor")
os.makedirs(TEMP_DIR, exist_ok=True)


def find_steam_save_locations():
    """Busca posibles carpetas de guardado de Dying Light en Steam (AppID 239140)."""
    candidates = []
    steam_roots = []
    if sys.platform == "win32":
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            val, _ = winreg.QueryValueEx(k, "SteamPath")
            if val and os.path.exists(val):
                steam_roots.append(os.path.normpath(val))
        except Exception:
            pass
        for drive in ["C", "D", "E", "F"]:
            p = f"{drive}:\\Program Files (x86)\\Steam"
            if p not in steam_roots and os.path.exists(p):
                steam_roots.append(p)
            p2 = f"{drive}:\\Steam"
            if p2 not in steam_roots and os.path.exists(p2):
                steam_roots.append(p2)

    for s_root in steam_roots:
        pattern = os.path.join(s_root, "userdata", "*", "239140", "remote", "out", "save")
        for match in glob.glob(pattern):
            if os.path.isdir(match) and match not in candidates:
                candidates.append(match)
    return candidates


def find_default_save_path():
    """Devuelve la ruta de guardado por defecto si existe, o None."""
    for save_dir in find_steam_save_locations():
        for fname in ["save_coop_0.sav", "save_coop_1.sav", "default.sav"]:
            candidate = os.path.join(save_dir, fname)
            if os.path.exists(candidate):
                return candidate
        savs = glob.glob(os.path.join(save_dir, "*.sav"))
        if savs:
            return savs[0]

    legacy = os.path.join(EDITOR_DIR, "save_coop_0.sav")
    if os.path.exists(legacy):
        return legacy

    return None
