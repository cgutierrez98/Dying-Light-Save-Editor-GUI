import os
import json
import shutil
from datetime import datetime
from logic.plugin_loader import get_base_path

CONFIG_FILE = os.path.join(get_base_path(), "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[CONFIG] Error loading config: {e}")
    return {}

def save_config(config_dict):
    tmp = CONFIG_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
        os.replace(tmp, CONFIG_FILE)
    except Exception as e:
        print(f"[CONFIG] Error saving config: {e}")

def create_save_backup(save_path):
    if not save_path or not os.path.exists(save_path):
        return None

    save_dir = os.path.dirname(save_path)
    backup_dir = os.path.join(save_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    base_name = os.path.basename(save_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_filename = f"{base_name}.bak_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        shutil.copy2(save_path, backup_path)
        print(f"[BACKUP] Created backup at {backup_path}")
        return backup_path
    except Exception as e:
        print(f"[BACKUP ERROR] Failed to create backup: {e}")
        return None

def list_save_backups(save_path):
    if not save_path:
        return []
    save_dir = os.path.dirname(save_path)
    backup_dir = os.path.join(save_dir, "backups")
    if not os.path.exists(backup_dir):
        return []

    base_name = os.path.basename(save_path)
    backups = []
    for f in os.listdir(backup_dir):
        if f.startswith(base_name + ".bak_"):
            full_path = os.path.join(backup_dir, f)
            backups.append(full_path)

    # Sort newest first
    backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return backups


MAX_BACKUPS = 30


def prune_backups(save_path, keep=MAX_BACKUPS):
    """Elimina los backups mas antiguos, conservando `keep`. El orden sale del timestamp del nombre."""
    removed = []
    backups = sorted(list_save_backups(save_path), key=os.path.basename, reverse=True)
    for old in backups[keep:]:
        try:
            os.remove(old)
            removed.append(old)
        except OSError as e:
            print(f"[BACKUP] Could not remove {old}: {e}")
    return removed


def atomic_replace(src, dst, keep_source=False):
    """Reemplaza `dst` por `src` de forma atomica.

    Copia primero a un temporal en la MISMA carpeta que `dst` (asi os.replace es atomico
    aunque src este en otra unidad) y luego lo renombra encima del destino.
    """
    tmp = os.path.join(os.path.dirname(os.path.abspath(dst)), f".{os.path.basename(dst)}.tmp_{os.getpid()}")
    try:
        shutil.copyfile(src, tmp)
        with open(tmp, "r+b") as f:
            os.fsync(f.fileno())
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
    if not keep_source:
        try:
            os.remove(src)
        except OSError:
            pass


