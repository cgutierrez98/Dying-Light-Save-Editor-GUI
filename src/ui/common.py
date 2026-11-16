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
SAMPLE_BAT = os.path.join(EDITOR_DIR, "sample.bat")
UPDATE_BAT = os.path.join(EDITOR_DIR, "update.bat")
DEFAULT_JSON = os.path.join(EDITOR_DIR, "save_coop_0.sav(edited).json")
SAVE_PATH = os.path.join(EDITOR_DIR, "save_coop_0.sav")
JSON_PATH = os.path.join(EDITOR_DIR, "save_coop_0.sav(edited).json")

# Carpetas y archivos temporales seguros
TEMP_DIR = os.path.join(tempfile.gettempdir(), "dying_light_save_editor")
os.makedirs(TEMP_DIR, exist_ok=True)
