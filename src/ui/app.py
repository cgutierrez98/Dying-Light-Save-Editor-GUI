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

from logic.batch import run_batch
from logic.cheats import (
    max_kings, max_quantity, max_skill, set_rarity, set_platinum,
    SOCKET_UPGRADES, get_duplicate_id_map, LEGEND_SKILLS,
    ORANGE_CRAFTPLANS, WEAPON_NAMES, COLLECTIBLES
)
from logic.plugin_loader import load_plugins
from logic.updater import check_updates_async
from logic.config import load_config, save_config, create_save_backup, list_save_backups
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
TEMP_JSON = os.path.join(TEMP_DIR, "._tmp.json")
TEMP_SAVE = os.path.join(TEMP_DIR, "._tmp.sav")


class SaveEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dying Light Save Editor GUI 1.6")
        self.geometry("1160x780")
        self.minsize(980, 640)

        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr

        self.config_data = load_config()
        self.editor_exe_path = self.config_data.get("editor_exe_path")

        saved_save_path = self.config_data.get("last_save_path")
        if saved_save_path and os.path.exists(saved_save_path):
            self.save_path = saved_save_path
        elif os.path.exists(SAVE_PATH):
            self.save_path = SAVE_PATH
        else:
            self.save_path = None

        self.json_path = DEFAULT_JSON
        self.current_data = None
        self.is_dirty = False
        self.is_busy = False

        self.weapon_map = {}
        self.inventory_map = {}
        self.skill_map = {}
        self.clipboard_data = None
        self.global_map = {}
        self.plugins = load_plugins()
        self.socket_options = SOCKET_UPGRADES
        self.console_visible = False

        self.weapon_tree = None
        self.inventory_tree = None
        self.stash_tree = None
        self.skills_tree = None
        self.current_tree = None
        self.search_entries = {}

        # Variables para el Inspector de Items
        self.inspector_active_item = None
        self.inspector_active_tree = None
        self.inspector_active_row = None

        # Aplicar tema oscuro moderno
        apply_dark_theme(self)

        self.create_menu()
        self.create_widgets()
        self.setup_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        check_updates_async(self)
        for plugin in self.plugins:
            if plugin.get("init_ui"):
                try:
                    plugin["init_ui"](self)
                except Exception as e:
                    print(f"[PLUGIN INIT ERROR] {plugin.get('name')}: {e}")

    # ==================== MENÚ SUPERIOR NATIVO ====================
    def create_menu(self):
        menubar = tk.Menu(self, bg=BG_SECONDARY, fg=FG_MAIN, activebackground=SELECTION_BG, activeforeground=FG_MAIN)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=BG_SECONDARY, fg=FG_MAIN, activebackground=SELECTION_BG, activeforeground=FG_MAIN)
        file_menu.add_command(label="Open Save...", accelerator="Ctrl+O", command=self.load_save)
        file_menu.add_command(label="Save Changes", accelerator="Ctrl+S", command=self.save_changes)
        file_menu.add_separator()
        file_menu.add_command(label="Backups / Restore...", command=self.show_backups_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=BG_SECONDARY, fg=FG_MAIN, activebackground=SELECTION_BG, activeforeground=FG_MAIN)
        edit_menu.add_command(label="➕ Add New Item...", accelerator="Ctrl+N", command=self.show_add_item_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy Item", accelerator="Ctrl+C", command=self._on_copy_shortcut)
        edit_menu.add_command(label="Paste Item", accelerator="Ctrl+V", command=self._on_paste_shortcut)
        edit_menu.add_command(label="Duplicate Item", accelerator="Ctrl+D", command=self._on_duplicate_shortcut)
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete Selected", accelerator="Del", command=self._on_delete_shortcut)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=BG_SECONDARY, fg=FG_MAIN, activebackground=SELECTION_BG, activeforeground=FG_MAIN)
        tools_menu.add_command(label="Configure Steffen CLI (editor.exe)...", command=self.select_editor_cli)
        tools_menu.add_command(label="Check Duplicate IDs", command=self.check_ids)
        tools_menu.add_separator()
        tools_menu.add_command(label="Toggle Debug Console", command=self.toggle_console)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=BG_SECONDARY, fg=FG_MAIN, activebackground=SELECTION_BG, activeforeground=FG_MAIN)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Download Steffen's CLI (Web)", command=lambda: webbrowser.open("https://steffenl.com/projects/dying-light-save-editor/releases"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    # ==================== WIDGETS Y LAYOUT ====================
    def create_widgets(self):
        # Barra superior limpia y moderna
        top_bar = tk.Frame(self, bg=BG_SECONDARY, padx=10, pady=6)
        top_bar.pack(fill=tk.X)

        # Botones de acción principales
        self.btn_save = ttk.Button(top_bar, text="💾 Save Changes", style="Accent.TButton", command=self.save_changes)
        self.btn_save.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_open = ttk.Button(top_bar, text="📂 Open Save", command=self.load_save)
        self.btn_open.pack(side=tk.LEFT, padx=3)

        btn_add = ttk.Button(top_bar, text="➕ Add Item", command=self.show_add_item_dialog)
        btn_add.pack(side=tk.LEFT, padx=3)

        btn_backup = ttk.Button(top_bar, text="🕒 Backups", command=self.show_backups_window)
        btn_backup.pack(side=tk.LEFT, padx=3)

        # Separador visual vertical
        sep = tk.Frame(top_bar, width=1, bg=BORDER_COLOR, height=22)
        sep.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Info de archivo cargado
        self.file_label = tk.Label(top_bar, text="No save file loaded", bg=BG_SECONDARY, fg=FG_MUTED, font=("Segoe UI", 9))
        self.file_label.pack(side=tk.LEFT, padx=5)

        # Insignia de estado modificado (Dirty state badge)
        self.dirty_badge = tk.Label(top_bar, text="", bg=BG_SECONDARY, font=("Segoe UI", 8, "bold"))
        self.dirty_badge.pack(side=tk.LEFT, padx=6)

        # Estado a la derecha
        self.status = tk.Label(top_bar, text="", bg=BG_SECONDARY, fg=ACCENT_BLUE, font=("Segoe UI", 9, "italic"))
        self.status.pack(side=tk.RIGHT, padx=5)

        # Barra de progreso indeterminada (sin bloqueos visuales)
        self.progress_bar = ttk.Progressbar(top_bar, mode="indeterminate", length=130)

        # Notebook principal (Pestañas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 6))

        self.tab_weapons = ttk.Frame(self.notebook)
        self.tab_inventory = ttk.Frame(self.notebook)
        self.tab_ammo = ttk.Frame(self.notebook)
        self.tab_skills = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)
        self.tab_stash = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_weapons, text="  ⚔️ Weapons  ")
        self.notebook.add(self.tab_inventory, text="  🎒 Inventory  ")
        self.notebook.add(self.tab_ammo, text="  🎯 Ammo  ")
        self.notebook.add(self.tab_skills, text="  ⭐ Skills  ")
        self.notebook.add(self.tab_stats, text="  📊 Stats & Money  ")
        self.notebook.add(self.tab_stash, text="  📦 Stash  ")

        def on_tab_changed(event):
            selected_tab = self.notebook.select()
            if selected_tab == str(self.tab_weapons):
                self.current_tree = self.weapon_tree
            elif selected_tab == str(self.tab_inventory):
                self.current_tree = self.inventory_tree
            elif selected_tab == str(self.tab_skills):
                self.current_tree = self.skills_tree
            elif selected_tab == str(self.tab_stash):
                self.current_tree = self.stash_tree

        self.notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

        # Plugins Frame (si existen plugins)
        if self.plugins:
            plugin_frame = tk.LabelFrame(self, text="Plugins", bg=BG_MAIN, fg=ACCENT_ORANGE, font=("Segoe UI", 9, "bold"))
            plugin_frame.pack(fill=tk.X, padx=8, pady=(0, 4))
            for plugin in self.plugins:
                ttk.Button(
                    plugin_frame,
                    text=plugin["name"],
                    command=lambda p=plugin: self.run_plugin(p)
                ).pack(side=tk.LEFT, padx=4, pady=3)

        # Consola de depuración integrada
        self.console = tk.Text(self, height=8, bg="#141414", fg="#dcdcdc", insertbackground=FG_MAIN, font=("Consolas", 9), relief="flat")
        sys.stdout = ConsoleRedirect(self.console, self._orig_stdout)
        sys.stderr = ConsoleRedirect(self.console, self._orig_stderr)

    # ==================== ATAJOS DE TECLADO ====================
    def setup_shortcuts(self):
        self.bind_all("<Control-o>", lambda e: self.load_save())
        self.bind_all("<Control-O>", lambda e: self.load_save())
        self.bind_all("<Control-s>", lambda e: self.save_changes())
        self.bind_all("<Control-S>", lambda e: self.save_changes())
        self.bind_all("<Control-n>", lambda e: self.show_add_item_dialog())
        self.bind_all("<Control-N>", lambda e: self.show_add_item_dialog())
        self.bind_all("<Control-f>", lambda e: self._on_search_shortcut())
        self.bind_all("<Control-F>", lambda e: self._on_search_shortcut())
        self.bind_all("<Control-c>", self._on_copy_shortcut)
        self.bind_all("<Control-C>", self._on_copy_shortcut)
        self.bind_all("<Control-v>", self._on_paste_shortcut)
        self.bind_all("<Control-V>", self._on_paste_shortcut)
        self.bind_all("<Control-d>", self._on_duplicate_shortcut)
        self.bind_all("<Control-D>", self._on_duplicate_shortcut)
        self.bind_all("<Delete>", self._on_delete_shortcut)

    def _is_text_widget_focused(self):
        focused = self.focus_get()
        return isinstance(focused, (tk.Entry, ttk.Entry, tk.Text, ttk.Combobox))

    def _on_copy_shortcut(self, event=None):
        if self._is_text_widget_focused():
            return
        if self.current_tree:
            self.copy_row(self.current_tree)

    def _on_paste_shortcut(self, event=None):
        if self._is_text_widget_focused():
            return
        if self.current_tree:
            self.paste_row(self.current_tree)

    def _on_duplicate_shortcut(self, event=None):
        if self._is_text_widget_focused():
            return
        if self.current_tree:
            self.duplicate_row(self.current_tree)

    def _on_delete_shortcut(self, event=None):
        if self._is_text_widget_focused():
            return
        selected_tab = self.notebook.select()
        if selected_tab == str(self.tab_skills):
            self.delete_selected_skills()

    def _on_search_shortcut(self):
        selected_tab = self.notebook.select()
        entry = self.search_entries.get(selected_tab)
        if entry:
            entry.focus_set()
            entry.selection_range(0, tk.END)

    # ==================== CONTROL DE CAMBIOS (DIRTY STATE) ====================
    def mark_dirty(self, dirty=True):
        self.is_dirty = dirty
        filename = os.path.basename(self.save_path) if self.save_path else "Untitled"
        if dirty:
            self.title(f"● Dying Light Save Editor GUI 1.6 - {filename} * (Unsaved Changes)")
            self.dirty_badge.config(text="● MODIFIED", fg=ACCENT_ORANGE)
        else:
            self.title(f"Dying Light Save Editor GUI 1.6 - {filename}")
            self.dirty_badge.config(text="✓ SAVED", fg="#4caf50")

    def check_unsaved_changes(self):
        if not self.is_dirty or not self.current_data:
            return True

        res = messagebox.askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes in your save file.\n\nDo you want to save your changes before proceeding?"
        )
        if res is True:
            self.save_changes(async_mode=False)
            return not self.is_dirty
        elif res is False:
            return True
        else:
            return False

    def set_busy(self, busy=True, status_text=""):
        self.is_busy = busy
        if busy:
            try:
                self.config(cursor="wait")
            except Exception:
                pass
            if status_text:
                self.set_status(status_text)
            self.progress_bar.pack(side=tk.RIGHT, padx=6)
            self.progress_bar.start(10)
            if hasattr(self, "btn_save"):
                self.btn_save.config(state="disabled")
            if hasattr(self, "btn_open"):
                self.btn_open.config(state="disabled")
        else:
            try:
                self.config(cursor="")
            except Exception:
                pass
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            if status_text:
                self.set_status(status_text)
            if hasattr(self, "btn_save"):
                self.btn_save.config(state="normal")
            if hasattr(self, "btn_open"):
                self.btn_open.config(state="normal")

    def set_status(self, text):
        self.status.config(text=text)
        self.update_idletasks()

    # ==================== DIÁLOGO AÑADIR ITEM DIRECTAMENTE ====================
    def show_add_item_dialog(self):
        if not self.current_data:
            messagebox.showinfo("Add Item", "Open a save file first before adding items.")
            return

        win = tk.Toplevel(self)
        win.title("➕ Add Item to Save File")
        win.geometry("660x600")
        win.configure(bg=BG_MAIN)
        win.transient(self)
        win.grab_set()

        # Header
        tk.Label(win, text="ADD NEW ITEM", bg=BG_MAIN, fg=ACCENT_ORANGE, font=("Segoe UI", 12, "bold")).pack(pady=(12, 4))
        tk.Label(win, text="Select an item from the catalog or type a custom ID:", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9)).pack()

        main_frame = tk.Frame(win, bg=BG_MAIN, padx=15, pady=8)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Filtro de categoría y buscador de catálogo
        filter_box = tk.Frame(main_frame, bg=BG_MAIN)
        filter_box.pack(fill=tk.X, pady=(0, 6))

        tk.Label(filter_box, text="Category:", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        categories_seen = []
        for it in ADD_ITEM_PRESETS:
            c = it.get("category", "General")
            if c not in categories_seen:
                categories_seen.append(c)
        categories = ["All Categories"] + categories_seen
        cat_var = tk.StringVar(value=categories[0])
        cat_menu = ttk.Combobox(filter_box, textvariable=cat_var, values=categories, state="readonly", width=22)
        cat_menu.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(filter_box, text="Search:", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        search_filter_var = tk.StringVar()
        search_filter_entry = ttk.Entry(filter_box, textvariable=search_filter_var, width=20)
        search_filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Lista de presets
        list_container = tk.Frame(main_frame, bg=BG_SECONDARY)
        list_container.pack(fill=tk.BOTH, expand=True, pady=4)

        preset_listbox = tk.Listbox(list_container, bg=BG_SECONDARY, fg=FG_MAIN, selectbackground=SELECTION_BG, selectforeground=FG_MAIN, font=("Segoe UI", 9), borderwidth=0, highlightthickness=0)
        sb_preset = ttk.Scrollbar(list_container, orient="vertical", command=preset_listbox.yview)
        preset_listbox.configure(yscrollcommand=sb_preset.set)

        preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_preset.pack(side=tk.RIGHT, fill=tk.Y)

        filtered_presets = []

        def refresh_preset_list(*args):
            preset_listbox.delete(0, tk.END)
            filtered_presets.clear()
            cat_filter = cat_var.get()
            q = search_filter_var.get().strip().lower()

            for item in ADD_ITEM_PRESETS:
                if cat_filter != "All Categories" and item.get("category") != cat_filter:
                    continue
                if q and (q not in item["name"].lower() and q not in item["id"].lower()):
                    continue
                filtered_presets.append(item)
                preset_listbox.insert(tk.END, f"  {item['name']}  [{item['id']}]  -  {item['category']}")

            if filtered_presets:
                preset_listbox.selection_set(0)
                on_preset_select()

        add_debounce = [None]

        def on_preset_search_change(*args):
            if add_debounce[0] is not None:
                win.after_cancel(add_debounce[0])
            add_debounce[0] = win.after(150, refresh_preset_list)

        cat_menu.bind("<<ComboboxSelected>>", refresh_preset_list)
        search_filter_var.trace_add("write", on_preset_search_change)

        # Formulario de parámetros del item seleccionado
        form_frame = tk.LabelFrame(main_frame, text="Item Parameters", bg=BG_CARD, fg=ACCENT_ORANGE, font=("Segoe UI", 9, "bold"), padx=12, pady=8)
        form_frame.pack(fill=tk.X, pady=(8, 0))

        # Item ID
        f_id = tk.Frame(form_frame, bg=BG_CARD)
        f_id.pack(fill=tk.X, pady=3)
        tk.Label(f_id, text="Internal ID:", bg=BG_CARD, fg=FG_MUTED, width=14, anchor="w").pack(side=tk.LEFT)
        id_var = tk.StringVar()
        id_entry = ttk.Entry(f_id, textvariable=id_var)
        id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Destino
        f_dest = tk.Frame(form_frame, bg=BG_CARD)
        f_dest.pack(fill=tk.X, pady=3)
        tk.Label(f_dest, text="Destination:", bg=BG_CARD, fg=FG_MUTED, width=14, anchor="w").pack(side=tk.LEFT)
        dest_var = tk.StringVar(value="Weapons (items1)")
        dest_menu = ttk.Combobox(f_dest, textvariable=dest_var, values=["Weapons (items1)", "Inventory Backpack (items3)", "Player Stash (storage)", "Ammo Slots (ammo)"], state="readonly")
        dest_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Cantidad y Rareza
        f_qty_rar = tk.Frame(form_frame, bg=BG_CARD)
        f_qty_rar.pack(fill=tk.X, pady=3)

        tk.Label(f_qty_rar, text="Quantity:", bg=BG_CARD, fg=FG_MUTED, width=14, anchor="w").pack(side=tk.LEFT)
        qty_var = tk.IntVar(value=1)
        ttk.Spinbox(f_qty_rar, from_=1, to=999999999, textvariable=qty_var, width=10).pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(f_qty_rar, text="Rarity:", bg=BG_CARD, fg=FG_MUTED).pack(side=tk.LEFT, padx=(0, 6))
        rarity_var = tk.StringVar(value="platinum")
        ttk.Combobox(f_qty_rar, textvariable=rarity_var, values=["white", "green", "blue", "violet", "orange", "platinum"], state="readonly", width=12).pack(side=tk.LEFT)

        # Opciones de Armas (4 Kings)
        kings_var = tk.BooleanVar(value=True)
        cb_kings = ttk.Checkbutton(form_frame, text="Equip 4 King Mods (Damage +2, Durability +2, Handling +2)", variable=kings_var)
        cb_kings.pack(anchor="w", pady=(4, 0))

        # Mapeo de munición conocida a IDs numéricos
        ammo_name_to_id = {
            "Ammo_Pistol": 43,
            "Ammo_Rifle": 44,
            "Ammo_Shotgun": 45,
            "Ammo_SMG": 1348,
            "Ammo_Arrow_Regular": 1335,
            "Ammo_Arrow_Fire": 1336,
            "Ammo_Arrow_Exploding": 1337,
            "Ammo_Arrow_Electric": 1340,
            "Ammo_Bolt_Regular": 2085,
            "Ammo_Bolt_Toxic": 2086,
            "Ammo_Bolt_Impact": 2088
        }

        def on_preset_select(event=None):
            sel = preset_listbox.curselection()
            if not sel or sel[0] >= len(filtered_presets):
                return
            chosen = filtered_presets[sel[0]]
            id_var.set(chosen["id"])
            qty_var.set(chosen.get("qty", 1))
            rarity_var.set(chosen.get("rarity", "platinum"))

            if chosen.get("category") == "Munición" or chosen["id"] in ammo_name_to_id:
                dest_var.set("Ammo Slots (ammo)")
                cb_kings.config(state="disabled")
            elif chosen.get("is_weapon", False):
                dest_var.set("Weapons (items1)")
                cb_kings.config(state="normal")
            else:
                dest_var.set("Inventory Backpack (items3)")
                cb_kings.config(state="disabled")

        preset_listbox.bind("<<ListboxSelect>>", on_preset_select)
        refresh_preset_list()

        # Acción Añadir
        def submit_add_item():
            item_id_str = id_var.get().strip()
            if not item_id_str:
                messagebox.showwarning("Missing ID", "Please specify an item ID.")
                return

            player = self.current_data.setdefault("player", {})
            inventory = player.setdefault("inventory", {})
            storage = player.setdefault("storage", {})
            dest = dest_var.get()

            # Caso especial: Munición directa en ammo slots
            if "Ammo Slots" in dest or item_id_str in ammo_name_to_id:
                numeric_ammo_id = ammo_name_to_id.get(item_id_str)
                if not numeric_ammo_id:
                    try:
                        numeric_ammo_id = int(item_id_str)
                    except ValueError:
                        numeric_ammo_id = 43  # fallback a pistola
                set_ammo_value(self.current_data, numeric_ammo_id, qty_var.get())
                self.mark_dirty(True)
                self.populate()
                disp = AMMO_DEFINITIONS.get(numeric_ammo_id, {}).get("name", item_id_str)
                messagebox.showinfo("Ammo Added", f"Successfully set ammo:\n{disp}\n\nAmount: {qty_var.get()}")
                win.destroy()
                return

            # Determinar ID numérico libre para armas/items
            all_existing = (
                inventory.get("items1", []) +
                inventory.get("quickSlots", []) +
                inventory.get("equipmentSlots", []) +
                inventory.get("items3", []) +
                storage.get("items1", []) +
                storage.get("items3", [])
            )
            existing_ids = [it.get("id", 0) for it in all_existing if isinstance(it, dict) and isinstance(it.get("id"), int)]
            new_numeric_id = (max(existing_ids) + 1) if existing_ids else 5000000

            # Construir item
            is_weapon = "Weapons" in dest or cb_kings.cget("state") == "normal"
            new_item = {
                "id": new_numeric_id,
                "name": item_id_str,
                "quantity": max(1, qty_var.get()),
                "attributes": {
                    "color": rarity_var.get()
                }
            }

            if is_weapon:
                new_item["condition"] = 999999.0
                new_item["repairs"] = 0
                new_item["craftPlan"] = "Craftplan_GodHammer"
                if kings_var.get():
                    new_item["upgradeSockets"] = ["Craft_Upgrade_DamL2DurL2BalL2"] * 4
                else:
                    new_item["upgradeSockets"] = []

            # Insertar en la lista destino
            if "items1" in dest:
                inventory.setdefault("items1", []).append(new_item)
            elif "items3" in dest:
                inventory.setdefault("items3", []).append(new_item)
            else:
                if is_weapon:
                    storage.setdefault("items1", []).append(new_item)
                else:
                    storage.setdefault("items3", []).append(new_item)

            self.mark_dirty(True)
            self.populate()
            disp = get_display_name(item_id_str)
            self.set_status(f"Added item: {disp}")
            messagebox.showinfo("Item Added", f"Successfully added item:\n{disp}\n\nAdded to: {dest}")
            win.destroy()

        # Botones inferiores
        btn_bar = tk.Frame(win, bg=BG_MAIN, pady=12, padx=15)
        btn_bar.pack(fill=tk.X)

        ttk.Button(btn_bar, text="➕ Add to Save File", style="Accent.TButton", command=submit_add_item).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_bar, text="Cancel", command=win.destroy).pack(side=tk.RIGHT, padx=5)

    # ==================== GESTIÓN DE ARCHIVOS Y CLI ====================
    def select_editor_cli(self):
        selected = filedialog.askopenfilename(
            title="Select Steffen's CLI (editor.exe)",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        if selected and os.path.exists(selected):
            self.editor_exe_path = selected
            self.config_data["editor_exe_path"] = selected
            save_config(self.config_data)
            messagebox.showinfo("CLI Configured", f"editor.exe set to:\n{selected}")

    def get_editor_exe(self):
        if self.editor_exe_path and os.path.exists(self.editor_exe_path):
            return self.editor_exe_path

        candidates = [
            os.path.join(EDITOR_DIR, "editor.exe"),
            os.path.join(EDITOR_DIR, "editor.exe.exe"),
            os.path.join(os.path.dirname(sys.executable), "editor.exe"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "editor.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                self.editor_exe_path = c
                self.config_data["editor_exe_path"] = c
                save_config(self.config_data)
                return c

        which_path = shutil.which("editor.exe") or shutil.which("editor")
        if which_path:
            self.editor_exe_path = which_path
            self.config_data["editor_exe_path"] = which_path
            save_config(self.config_data)
            return which_path

        res = messagebox.askyesno(
            "CLI Steffen Requerido",
            "No se encontró 'editor.exe' (el CLI de Steffen necesario para desencriptar saves).\n\n"
            "¿Deseas buscar y seleccionar 'editor.exe' manualmente?\n\n"
            "(Si no lo tienes, descárgalo de https://steffenl.com/projects/dying-light-save-editor/releases)"
        )
        if res:
            selected = filedialog.askopenfilename(
                title="Selecciona editor.exe (CLI de Steffen)",
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
            )
            if selected and os.path.exists(selected):
                self.editor_exe_path = selected
                self.config_data["editor_exe_path"] = selected
                save_config(self.config_data)
                return selected

        return None

    def _run_editor(self, args):
        editor_exe = self.get_editor_exe()
        if not editor_exe:
            return None
        try:
            cwd = os.path.dirname(editor_exe) if os.path.exists(editor_exe) else (EDITOR_DIR if os.path.exists(EDITOR_DIR) else None)
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW
            return subprocess.run(
                [editor_exe, *args],
                cwd=cwd,
                capture_output=True,
                creationflags=creationflags
            )
        except Exception as e:
            print(f"[ERROR] _run_editor: {e}")
            return None

    def load_save(self, ask_file=True, target_path=None):
        if self.is_busy:
            return

        if not self.check_unsaved_changes():
            return

        path = target_path
        if ask_file or not path:
            if not path and not ask_file and self.save_path:
                path = self.save_path
            else:
                initial_dir = os.path.dirname(self.save_path) if self.save_path else (EDITOR_DIR if os.path.exists(EDITOR_DIR) else None)
                path = filedialog.askopenfilename(
                    title="Select Dying Light Save File",
                    initialdir=initial_dir,
                    filetypes=[("Dying Light Save", "*.sav"), ("All files", "*.*")]
                )
                if not path:
                    return

        if not path or not os.path.exists(path):
            messagebox.showerror("Error", f"No valid .sav file selected:\n{path}")
            return

        self.set_busy(True, "Decrypting save file with Steffen CLI...")

        threading.Thread(
            target=self._worker_load_save,
            args=(path,),
            daemon=True
        ).start()

    def _worker_load_save(self, path):
        try:
            ret = self._run_editor([
                "sample",
                path,
                f"--patch={TEMP_JSON}"
            ])

            if ret is None or ret.returncode != 0:
                self.after(0, lambda: self._on_load_error(
                    "Could not decrypt the selected .sav file.\nMake sure editor.exe is the CLI by Steffen."
                ))
                return

            if not os.path.exists(TEMP_JSON):
                self.after(0, lambda: self._on_load_error(
                    "Could not decrypt the selected .sav file.\nTemporary JSON file was not generated."
                ))
                return

            with open(TEMP_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.after(0, lambda: self._on_load_success(path, data))
        except Exception as e:
            self.after(0, lambda: self._on_load_error(f"Error reading save data:\n{e}"))

    def _on_load_success(self, path, data):
        self.save_path = path
        self.config_data["last_save_path"] = self.save_path
        save_config(self.config_data)

        self.current_data = data
        self.file_label.config(text=os.path.basename(self.save_path), fg=FG_MAIN)
        self.mark_dirty(False)
        self.populate()
        self.set_busy(False, f"Loaded: {os.path.basename(path)}")

    def _on_load_error(self, err_msg):
        self.set_busy(False, "")
        messagebox.showerror("Error", err_msg)

    def save_changes(self, async_mode=True, on_success=None):
        if self.is_busy:
            return

        if not self.current_data or not self.save_path:
            messagebox.showwarning("Warning", "No save loaded to save changes.")
            return

        self.focus()

        # Tomamos snapshot profundo para que el hilo de guardado trabaje sin interferencias
        data_snapshot = copy.deepcopy(self.current_data)
        save_path = self.save_path

        self.set_busy(True, "Creating backup and encrypting save...")

        if async_mode:
            threading.Thread(
                target=self._worker_save_changes,
                args=(save_path, data_snapshot, on_success, True),
                daemon=True
            ).start()
        else:
            self._worker_save_changes(save_path, data_snapshot, on_success, False)

    def _worker_save_changes(self, save_path, data_snapshot, on_success, is_async=True):
        try:
            # 1. Crear backup automático
            backup_file = create_save_backup(save_path)

            # 2. Escribir JSON temporal
            with open(TEMP_JSON, "w", encoding="utf-8") as f:
                json.dump(data_snapshot, f, indent=4)
                f.flush()
                os.fsync(f.fileno())

            # 3. Compilar y encriptar archivo .sav con Steffen CLI
            ret = self._run_editor([
                "update",
                save_path,
                f"--patch={TEMP_JSON}",
                f"--output={TEMP_SAVE}"
            ])

            if ret is None or ret.returncode != 0 or not os.path.exists(TEMP_SAVE):
                err = "Could not update the .sav file with Steffen's CLI."
                if is_async:
                    self.after(0, lambda: self._on_save_error(err))
                else:
                    self._on_save_error(err)
                return

            # 4. Reemplazar archivo .sav original de forma segura
            shutil.move(TEMP_SAVE, save_path)

            if is_async:
                self.after(0, lambda: self._on_save_success(save_path, backup_file, on_success))
            else:
                self._on_save_success(save_path, backup_file, on_success)

        except Exception as e:
            err = f"Failed to save changes:\n{e}"
            if is_async:
                self.after(0, lambda: self._on_save_error(err))
            else:
                self._on_save_error(err)

    def _on_save_success(self, save_path, backup_file, on_success):
        self.mark_dirty(False)
        self.set_busy(False, f"Saved: {os.path.basename(save_path)}")
        self.cleanup()

        backup_info = f"\n\nAutomatic backup created:\n{os.path.basename(backup_file)}" if backup_file else ""
        messagebox.showinfo(
            "Saved",
            f"Changes successfully saved to {os.path.basename(save_path)}!{backup_info}"
        )

        if on_success:
            on_success()

    def _on_save_error(self, err_msg):
        self.set_busy(False, "")
        messagebox.showerror("Error", err_msg)

    def show_backups_window(self):
        if not self.save_path:
            messagebox.showinfo("Backups", "Open a save file first to view its backups.")
            return

        backups = list_save_backups(self.save_path)
        win = tk.Toplevel(self)
        win.title(f"Backups - {os.path.basename(self.save_path)}")
        win.geometry("620x400")
        win.configure(bg=BG_MAIN)
        win.transient(self)

        tk.Label(win, text=f"Available Backups for: {os.path.basename(self.save_path)}", bg=BG_MAIN, fg=ACCENT_ORANGE, font=("Segoe UI", 11, "bold")).pack(pady=10)

        if not backups:
            tk.Label(win, text="No automatic backups found for this save file yet.\nBackups are created automatically every time you click 'Save Changes'.", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9)).pack(pady=40)
            ttk.Button(win, text="Close", command=win.destroy).pack(pady=10)
            return

        list_frame = tk.Frame(win, bg=BG_SECONDARY, padx=2, pady=2)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=5)

        lb = tk.Listbox(list_frame, bg=BG_SECONDARY, fg=FG_MAIN, selectbackground=SELECTION_BG, selectforeground=FG_MAIN, font=("Consolas", 9), borderwidth=0, highlightthickness=0)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=sb.set)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        for b in backups:
            mtime = datetime.fromtimestamp(os.path.getmtime(b)).strftime("%Y-%m-%d %H:%M:%S")
            size_kb = os.path.getsize(b) / 1024
            lb.insert(tk.END, f" {os.path.basename(b)}  ({mtime}, {size_kb:.1f} KB)")
        lb.selection_set(0)

        def restore_selected():
            sel = lb.curselection()
            if not sel:
                return
            chosen_backup = backups[sel[0]]
            if messagebox.askyesno(
                "Restore Backup",
                f"Are you sure you want to restore this backup?\n\n{os.path.basename(chosen_backup)}\n\nThis will replace your current save file!"
            ):
                try:
                    create_save_backup(self.save_path)
                    shutil.copy2(chosen_backup, self.save_path)
                    messagebox.showinfo("Restored", "Backup restored successfully! Reloading save...")
                    win.destroy()
                    self.load_save(ask_file=False)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to restore backup:\n{e}")

        btn_box = tk.Frame(win, bg=BG_MAIN)
        btn_box.pack(fill=tk.X, pady=12, padx=12)
        ttk.Button(btn_box, text="Restore Selected Backup", style="Accent.TButton", command=restore_selected).pack(side=tk.LEFT)
        ttk.Button(btn_box, text="Close", command=win.destroy).pack(side=tk.RIGHT)

    # ==================== POPULATE & TABS ====================
    def populate(self):
        for tab in (self.tab_weapons, self.tab_inventory, self.tab_ammo, self.tab_skills, self.tab_stats, self.tab_stash):
            for widget in tab.winfo_children():
                widget.destroy()

        if not self.current_data:
            return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})
        storage = player.get("storage", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", [])
        )

        weapons = [
            item for item in all_items
            if isinstance(item, dict)
        ]
        items = inventory.get("items3", [])
        stash_items = (
            storage.get("items1", []) +
            storage.get("items3", [])
        )

        self.weapon_map.clear()
        self.inventory_map.clear()
        self.skill_map.clear()
        self.global_map.clear()
        self.search_entries.clear()

        # ==================== WEAPONS TAB (Con Inspector Master-Detail) ====================
        weapon_toolbar = tk.Frame(self.tab_weapons, bg=BG_MAIN)
        weapon_toolbar.pack(fill=tk.X, padx=6, pady=4)

        ttk.Button(weapon_toolbar, text="➕ Add Weapon", style="Accent.TButton", command=self.show_add_item_dialog).pack(side=tk.LEFT, padx=3)
        ttk.Button(weapon_toolbar, text="⚡ Powerful Weapon", command=self.set_unknown008).pack(side=tk.LEFT, padx=3)
        ttk.Button(weapon_toolbar, text="🛡️ Max Condition & Reset Repairs", command=self.max_weapon_stats).pack(side=tk.LEFT, padx=3)
        ttk.Button(weapon_toolbar, text="💎 All Platinum", command=self.set_all_platinum).pack(side=tk.LEFT, padx=3)
        ttk.Button(weapon_toolbar, text="🔥 OP Craft Combo", command=self.set_op_craft_combo).pack(side=tk.LEFT, padx=3)

        # PanedWindow para dividir la tabla (izq) y el Inspector (der)
        weapons_paned = ttk.PanedWindow(self.tab_weapons, orient=tk.HORIZONTAL)
        weapons_paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        weapons_left = ttk.Frame(weapons_paned)
        weapons_right = tk.Frame(weapons_paned, bg=BG_CARD, padx=12, pady=10, relief="solid", borderwidth=1)
        weapons_paned.add(weapons_left, weight=3)
        weapons_paned.add(weapons_right, weight=2)

        self.weapon_tree = self.create_table(
            weapons_left,
            ["name", "quantity", "condition", "repairs", "id", "craftPlan", "upgradeSockets"],
            weapons,
            self.weapon_map,
            tab_key=str(self.tab_weapons),
            on_select_callback=lambda item, tree, row_id: self.update_item_inspector(weapons_right, item, tree, row_id)
        )

        self.render_inspector_placeholder(weapons_right)

        # ==================== INVENTORY TAB ====================
        inv_toolbar = tk.Frame(self.tab_inventory, bg=BG_MAIN)
        inv_toolbar.pack(fill=tk.X, padx=6, pady=4)

        ttk.Button(inv_toolbar, text="➕ Add Item", style="Accent.TButton", command=self.show_add_item_dialog).pack(side=tk.LEFT, padx=3)
        ttk.Button(inv_toolbar, text="💎 All Platinum", command=self.set_all_platinum).pack(side=tk.LEFT, padx=3)
        ttk.Button(inv_toolbar, text="⚡ Powerful Weapon", command=self.set_unknown008).pack(side=tk.LEFT, padx=3)
        ttk.Button(inv_toolbar, text="🎁 Add All Collectibles", command=self.add_collectibles).pack(side=tk.LEFT, padx=3)
        ttk.Button(inv_toolbar, text="Max Amount Selected", command=self.max_amount).pack(side=tk.LEFT, padx=3)

        self.inventory_tree = self.create_table(
            self.tab_inventory,
            ["name", "quantity", "id", "craftPlan", "upgradeSockets"],
            items,
            self.inventory_map,
            tab_key=str(self.tab_inventory)
        )

        # ==================== AMMO TAB (MUNICIÓN DEDICADA) ====================
        self.create_ammo_tab(self.tab_ammo)

        # ==================== SKILLS TAB ====================
        skills_toolbar = tk.Frame(self.tab_skills, bg=BG_MAIN)
        skills_toolbar.pack(fill=tk.X, padx=6, pady=4)

        ttk.Button(skills_toolbar, text="⭐ Add All Legend Skills", style="Accent.TButton", command=self.add_legend_skills).pack(side=tk.LEFT, padx=3)

        self.special_skill_var = tk.StringVar(value="ZombieSprintUpgrade")
        skill_dropdown = ttk.Combobox(
            skills_toolbar,
            textvariable=self.special_skill_var,
            values=["ZombieSprintUpgrade", "ZombieRopeLocoUpgrade"],
            state="readonly",
            width=24
        )
        skill_dropdown.pack(side=tk.LEFT, padx=4)

        ttk.Button(skills_toolbar, text="Add Special Skill", command=self.add_special_skill).pack(side=tk.LEFT, padx=3)
        ttk.Button(skills_toolbar, text="🗑️ Delete Selected", command=self.delete_selected_skills).pack(side=tk.LEFT, padx=3)

        skills_container = tk.Frame(self.tab_skills, bg=BG_MAIN)
        skills_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        self.skills_tree = ttk.Treeview(skills_container, columns=("name", "stacks"), show="headings", selectmode="extended")
        self.skills_tree.heading("name", text="Skill Name")
        self.skills_tree.heading("stacks", text="Stacks / Level")
        self.skills_tree.column("name", width=340)
        self.skills_tree.column("stacks", width=120)

        vsb_skills = ttk.Scrollbar(skills_container, orient="vertical", command=self.skills_tree.yview)
        self.skills_tree.configure(yscrollcommand=vsb_skills.set)

        self.skills_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb_skills.pack(side=tk.RIGHT, fill=tk.Y)

        self.skills_tree.bind("<Double-1>", lambda e: self.edit_cell(e, self.skills_tree, ("name", "stacks")))
        self.skills_tree.bind("<Button-1>", lambda e: setattr(self, "current_tree", self.skills_tree))

        for buff in player.get("buffs", []):
            name = buff.get("name", "")
            if not name.endswith("_skill"):
                continue

            raw_base = name.replace("_skill", "")
            disp_skill = ITEM_DICTIONARY.get(raw_base, raw_base.replace("_", " "))

            item_id = self.skills_tree.insert("", "end", values=(
                f"{disp_skill} [{raw_base}]",
                buff.get("stacks", 0)
            ))
            self.skill_map[item_id] = buff
            self.global_map[(self.skills_tree, item_id)] = (None, None, buff)

        # ==================== STATS TAB ====================
        self.create_stats(self.tab_stats, player)

        # ==================== STASH TAB ====================
        stash_toolbar = tk.Frame(self.tab_stash, bg=BG_MAIN)
        stash_toolbar.pack(fill=tk.X, padx=6, pady=4)

        ttk.Button(stash_toolbar, text="➕ Add to Stash", style="Accent.TButton", command=self.show_add_item_dialog).pack(side=tk.LEFT, padx=3)
        ttk.Button(stash_toolbar, text="💎 All Platinum", command=self.set_all_platinum).pack(side=tk.LEFT, padx=3)
        ttk.Button(stash_toolbar, text="⚡ Powerful Weapon", command=self.set_unknown008).pack(side=tk.LEFT, padx=3)
        ttk.Button(stash_toolbar, text="🔥 OP Craft Combo", command=self.set_op_craft_combo).pack(side=tk.LEFT, padx=3)

        self.stash_tree = self.create_table(
            self.tab_stash,
            ["name", "quantity", "id", "craftPlan", "upgradeSockets"],
            stash_items,
            self.inventory_map,
            tab_key=str(self.tab_stash)
        )

        # Establecer árbol activo según la pestaña visible
        selected_tab = self.notebook.select() if hasattr(self, "notebook") else None
        if selected_tab == str(self.tab_inventory):
            self.current_tree = self.inventory_tree
        elif selected_tab == str(self.tab_skills):
            self.current_tree = self.skills_tree
        elif selected_tab == str(self.tab_stash):
            self.current_tree = self.stash_tree
        else:
            self.current_tree = self.weapon_tree

    # ==================== PESTAÑA DEDICADA DE MUNICIONES ====================
    def create_ammo_tab(self, parent):
        toolbar = tk.Frame(parent, bg=BG_MAIN)
        toolbar.pack(fill=tk.X, padx=10, pady=8)

        def on_max_all():
            max_all_ammo(self.current_data, 9999)
            self.mark_dirty(True)
            self.populate()
            self.set_status("All ammo set to 9999!")

        ttk.Button(toolbar, text="⚡ Max All Ammo (9999)", style="Accent.TButton", command=on_max_all).pack(side=tk.LEFT, padx=3)

        tk.Label(toolbar, text="💡 Ammo is equipped directly into your character's weapon ammo slots.", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9, "italic")).pack(side=tk.LEFT, padx=12)

        # Contenedor con scroll para las municiones
        scroll_container = tk.Frame(parent, bg=BG_MAIN)
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas = tk.Canvas(scroll_container, bg=BG_MAIN, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas, bg=BG_MAIN)

        inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ammo_list = get_ammo_data(self.current_data)

        # Grid de 2 columnas con tarjetas para cada tipo de munición
        for idx, item in enumerate(ammo_list):
            ammo_id = item["id"]
            card = tk.Frame(inner_frame, bg=BG_CARD, padx=14, pady=10, relief="solid", borderwidth=1)
            row = idx // 2
            col = idx % 2
            card.grid(row=row, column=col, padx=8, pady=6, sticky="ew")
            inner_frame.grid_columnconfigure(col, weight=1)

            # Icono + Nombre
            title_box = tk.Frame(card, bg=BG_CARD)
            title_box.pack(fill=tk.X, pady=(0, 6))

            tk.Label(title_box, text=f"{item['icon']} {item['name']}", bg=BG_CARD, fg=FG_MAIN, font=("Segoe UI", 10, "bold"), anchor="w").pack(side=tk.LEFT)
            tk.Label(title_box, text=f"Ammo ID: {ammo_id}", bg=BG_CARD, fg=FG_MUTED, font=("Consolas", 8)).pack(side=tk.RIGHT)

            # Control de cantidad
            ctrl_box = tk.Frame(card, bg=BG_CARD)
            ctrl_box.pack(fill=tk.X)

            tk.Label(ctrl_box, text="Quantity:", bg=BG_CARD, fg=FG_MUTED, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 6))

            qty_var = tk.IntVar(value=item["value"])
            spin = ttk.Spinbox(ctrl_box, from_=0, to=99999, textvariable=qty_var, width=10)
            spin.pack(side=tk.LEFT, padx=(0, 8))

            def make_save_ammo(aid, qv):
                def save_ammo(e=None):
                    try:
                        val = int(qv.get())
                        set_ammo_value(self.current_data, aid, val)
                        self.mark_dirty(True)
                    except ValueError:
                        pass
                return save_ammo

            save_fn = make_save_ammo(ammo_id, qty_var)
            spin.bind("<FocusOut>", save_fn)
            spin.bind("<Return>", save_fn)

            def make_max_single(aid, qv, sfn):
                def max_single():
                    qv.set(9999)
                    sfn()
                return max_single

            ttk.Button(ctrl_box, text="Max (9999)", command=make_max_single(ammo_id, qty_var, save_fn)).pack(side=tk.LEFT)

    # ==================== PANEL INSPECTOR LATERAL (MASTER-DETAIL) ====================
    def render_inspector_placeholder(self, parent):
        for w in parent.winfo_children():
            w.destroy()
        placeholder = tk.Label(
            parent,
            text="🔍 Select an item from the list\nto inspect and edit its properties visually",
            bg=BG_CARD,
            fg=FG_MUTED,
            font=("Segoe UI", 10),
            justify="center"
        )
        placeholder.pack(expand=True, fill=tk.BOTH, pady=40)

    def update_item_inspector(self, parent, item, tree, row_id):
        self.inspector_active_item = item
        self.inspector_active_tree = tree
        self.inspector_active_row = row_id

        for w in parent.winfo_children():
            w.destroy()

        if not item or not isinstance(item, dict):
            self.render_inspector_placeholder(parent)
            return

        # Encabezado del Inspector
        header_frame = tk.Frame(parent, bg=BG_CARD)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(header_frame, text="ITEM INSPECTOR", bg=BG_CARD, fg=ACCENT_ORANGE, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        # Insignia de Rareza
        attrs = item.setdefault("attributes", {})
        current_rarity = attrs.get("color", "white").lower()
        badge_color = RARITY_COLORS.get(current_rarity, "#ffffff")

        rarity_badge = tk.Label(
            header_frame,
            text=f" {current_rarity.upper()} ",
            bg=badge_color,
            fg="#000000" if current_rarity in ["white", "platinum", "green"] else "#ffffff",
            font=("Segoe UI", 8, "bold"),
            padx=4,
            pady=2
        )
        rarity_badge.pack(side=tk.RIGHT)

        # Selector de Nombre
        f_name = tk.Frame(parent, bg=BG_CARD)
        f_name.pack(fill=tk.X, pady=4)
        tk.Label(f_name, text="Name:", bg=BG_CARD, fg=FG_MUTED, width=10, anchor="w").pack(side=tk.LEFT)
        name_var = tk.StringVar(value=item.get("name", ""))
        name_entry = ttk.Combobox(f_name, textvariable=name_var, values=WEAPON_NAMES)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def on_name_change(e=None):
            new_n = name_var.get().strip()
            if new_n and new_n != item.get("name"):
                item["name"] = new_n
                self.mark_dirty(True)
                self.refresh_tree_row(tree, row_id, item)
        name_entry.bind("<FocusOut>", on_name_change)
        name_entry.bind("<<ComboboxSelected>>", on_name_change)

        # Selector de Rareza
        f_rar = tk.Frame(parent, bg=BG_CARD)
        f_rar.pack(fill=tk.X, pady=4)
        tk.Label(f_rar, text="Rarity:", bg=BG_CARD, fg=FG_MUTED, width=10, anchor="w").pack(side=tk.LEFT)
        rarity_var = tk.StringVar(value=current_rarity)
        rarity_combo = ttk.Combobox(f_rar, textvariable=rarity_var, values=["white", "green", "blue", "violet", "orange", "platinum"], state="readonly")
        rarity_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def on_rarity_change(e=None):
            new_r = rarity_var.get()
            set_rarity(item, new_r)
            b_color = RARITY_COLORS.get(new_r, "#ffffff")
            rarity_badge.config(
                text=f" {new_r.upper()} ",
                bg=b_color,
                fg="#000000" if new_r in ["white", "platinum", "green"] else "#ffffff"
            )
            self.mark_dirty(True)
            self.refresh_tree_row(tree, row_id, item)
        rarity_combo.bind("<<ComboboxSelected>>", on_rarity_change)

        # Durabilidad / Condición
        if "condition" in item:
            f_dur = tk.Frame(parent, bg=BG_CARD)
            f_dur.pack(fill=tk.X, pady=4)
            tk.Label(f_dur, text="Condition:", bg=BG_CARD, fg=FG_MUTED, width=10, anchor="w").pack(side=tk.LEFT)

            dur_var = tk.StringVar(value=str(item.get("condition", 100.0)))
            dur_entry = ttk.Entry(f_dur, textvariable=dur_var, width=10)
            dur_entry.pack(side=tk.LEFT, padx=(0, 6))

            def on_dur_change(e=None):
                try:
                    val = float(dur_var.get())
                    item["condition"] = val
                    self.mark_dirty(True)
                    self.refresh_tree_row(tree, row_id, item)
                except ValueError:
                    pass
            dur_entry.bind("<FocusOut>", on_dur_change)

            ttk.Button(
                f_dur,
                text="Full Repair",
                command=lambda: [dur_var.set("999999"), on_dur_change()]
            ).pack(side=tk.LEFT)

        # Reparaciones Restantes
        if "repairs" in item:
            f_rep = tk.Frame(parent, bg=BG_CARD)
            f_rep.pack(fill=tk.X, pady=4)
            tk.Label(f_rep, text="Repairs:", bg=BG_CARD, fg=FG_MUTED, width=10, anchor="w").pack(side=tk.LEFT)

            rep_var = tk.IntVar(value=item.get("repairs", 0))
            rep_spin = ttk.Spinbox(f_rep, from_=0, to=100, textvariable=rep_var, width=6)
            rep_spin.pack(side=tk.LEFT, padx=(0, 6))

            def on_rep_change(e=None):
                try:
                    val = int(rep_var.get())
                    item["repairs"] = val
                    self.mark_dirty(True)
                    self.refresh_tree_row(tree, row_id, item)
                except ValueError:
                    pass
            rep_spin.bind("<FocusOut>", on_rep_change)

            ttk.Button(
                f_rep,
                text="Reset (0)",
                command=lambda: [rep_var.set(0), on_rep_change()]
            ).pack(side=tk.LEFT)

        # Cantidad
        f_qty = tk.Frame(parent, bg=BG_CARD)
        f_qty.pack(fill=tk.X, pady=4)
        tk.Label(f_qty, text="Quantity:", bg=BG_CARD, fg=FG_MUTED, width=10, anchor="w").pack(side=tk.LEFT)

        qty_var = tk.IntVar(value=item.get("quantity", 1))
        qty_spin = ttk.Spinbox(f_qty, from_=1, to=999999999, textvariable=qty_var, width=10)
        qty_spin.pack(side=tk.LEFT, padx=(0, 6))

        def on_qty_change(e=None):
            try:
                val = int(qty_var.get())
                item["quantity"] = val
                self.mark_dirty(True)
                self.refresh_tree_row(tree, row_id, item)
            except ValueError:
                pass
        qty_spin.bind("<FocusOut>", on_qty_change)

        ttk.Button(
            f_qty,
            text="Max (999M)",
            command=lambda: [qty_var.set(999999999), on_qty_change()]
        ).pack(side=tk.LEFT)

        # Craftplan
        f_cp = tk.Frame(parent, bg=BG_CARD)
        f_cp.pack(fill=tk.X, pady=4)
        tk.Label(f_cp, text="Craftplan:", bg=BG_CARD, fg=FG_MUTED, width=10, anchor="w").pack(side=tk.LEFT)
        cp_var = tk.StringVar(value=item.get("craftPlan", ""))
        cp_combo = ttk.Combobox(f_cp, textvariable=cp_var, values=ORANGE_CRAFTPLANS)
        cp_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def on_cp_change(e=None):
            item["craftPlan"] = cp_var.get().strip()
            self.mark_dirty(True)
            self.refresh_tree_row(tree, row_id, item)
        cp_combo.bind("<FocusOut>", on_cp_change)
        cp_combo.bind("<<ComboboxSelected>>", on_cp_change)

        # Separador para sockets
        tk.Frame(parent, bg=BORDER_COLOR, height=1).pack(fill=tk.X, pady=8)

        # Slots de Mejoras (Visual Mod Slots)
        sockets_header = tk.Frame(parent, bg=BG_CARD)
        sockets_header.pack(fill=tk.X, pady=(0, 6))

        tk.Label(sockets_header, text="UPGRADE SOCKETS", bg=BG_CARD, fg=ACCENT_ORANGE, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        # Botón Max 4 Kings directo
        def equip_4_kings():
            max_kings(item)
            self.mark_dirty(True)
            self.refresh_tree_row(tree, row_id, item)
            self.update_item_inspector(parent, item, tree, row_id)

        ttk.Button(sockets_header, text="👑 4 Kings", style="Accent.TButton", command=equip_4_kings).pack(side=tk.RIGHT)

        sockets_list = item.setdefault("upgradeSockets", [])

        # Mostrar 4 sockets fijos para edición visual
        for slot_idx in range(4):
            f_slot = tk.Frame(parent, bg=BG_CARD)
            f_slot.pack(fill=tk.X, pady=2)

            tk.Label(f_slot, text=f"Slot {slot_idx+1}:", bg=BG_CARD, fg=FG_MUTED, width=8, anchor="w").pack(side=tk.LEFT)

            current_mod = sockets_list[slot_idx] if slot_idx < len(sockets_list) else "(Empty)"
            slot_var = tk.StringVar(value=current_mod)

            combo_values = ["(Empty)"] + SOCKET_UPGRADES
            combo_slot = ttk.Combobox(f_slot, textvariable=slot_var, values=combo_values, state="readonly")
            combo_slot.pack(side=tk.LEFT, fill=tk.X, expand=True)

            def make_slot_handler(idx, v):
                def handler(e=None):
                    chosen = v.get()
                    while len(sockets_list) <= idx:
                        sockets_list.append("")
                    if chosen == "(Empty)":
                        sockets_list[idx] = ""
                    else:
                        sockets_list[idx] = chosen

                    # Filtrar vacíos finales
                    while sockets_list and not sockets_list[-1]:
                        sockets_list.pop()

                    item["upgradeSockets"] = sockets_list
                    self.mark_dirty(True)
                    self.refresh_tree_row(tree, row_id, item)
                return handler

            combo_slot.bind("<<ComboboxSelected>>", make_slot_handler(slot_idx, slot_var))

    def refresh_tree_row(self, tree, row_id, item):
        columns = tree["columns"]
        values = []
        for col in columns:
            if col == "name":
                raw_n = item.get("name", "")
                values.append(get_display_name(raw_n))
            elif col == "stacks":
                if "stacks" in item:
                    values.append(item["stacks"])
                elif "unknown" in item and "unknown001" in item.get("unknown", {}):
                    values.append(item["unknown"]["unknown001"])
                else:
                    values.append("")
            elif col == "craftPlan":
                raw_cp = item.get("craftPlan", "")
                values.append(get_craftplan_display_name(raw_cp))
            elif col == "upgradeSockets":
                socks = item.get("upgradeSockets", [])
                disp_socks = [get_socket_display_name(s) for s in socks if s]
                values.append(", ".join(disp_socks))
            else:
                values.append(item.get(col, ""))
        tree.item(row_id, values=values)

    # ==================== TABLA Y FILTRADO ====================
    def create_table(self, parent, columns, data, map_ref, tab_key=None, on_select_callback=None):
        container = tk.Frame(parent, bg=BG_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        # Buscador y filtro en tiempo real
        search_frame = tk.Frame(container, bg=BG_MAIN)
        search_frame.pack(fill=tk.X, pady=(0, 4))

        tk.Label(search_frame, text="🔍 Filter:", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(2, 4))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=28)
        search_entry.pack(side=tk.LEFT, padx=2)

        if tab_key:
            self.search_entries[tab_key] = search_entry

        debounce_timer = [None]

        def clear_search():
            if debounce_timer[0] is not None:
                self.after_cancel(debounce_timer[0])
                debounce_timer[0] = None
            search_var.set("")
            populate_tree_rows("")

        clear_btn = ttk.Button(search_frame, text="Clear", command=clear_search)
        clear_btn.pack(side=tk.LEFT, padx=4)

        search_entry.bind("<Return>", lambda e: (
            self.after_cancel(debounce_timer[0]) if debounce_timer[0] is not None else None,
            populate_tree_rows(search_var.get())
        ))

        count_label = tk.Label(search_frame, text=f"{len(data)} items", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9))
        count_label.pack(side=tk.RIGHT, padx=5)

        # Contenedor de la tabla con Scrollbars
        table_frame = tk.Frame(container, bg=BG_MAIN)
        table_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=140 if col != "name" else 220, minwidth=60)

        # Menú contextual (Clic Derecho)
        menu = tk.Menu(tree, tearoff=0, bg=BG_SECONDARY, fg=FG_MAIN, activebackground=SELECTION_BG, activeforeground=FG_MAIN)
        menu.add_command(label="➕ Add New Item...", command=self.show_add_item_dialog)
        menu.add_separator()
        menu.add_command(label="Copy Item", command=lambda: self.copy_row(tree))
        menu.add_command(label="Paste Item", command=lambda: self.paste_row(tree))
        menu.add_command(label="Duplicate Item", command=lambda: self.duplicate_row(tree))

        def show_menu(event):
            row = tree.identify_row(event.y)
            if row:
                if row not in tree.selection():
                    tree.selection_set(row)
                menu.post(event.x_root, event.y_root)

        tree.bind("<Button-3>", show_menu)
        tree.bind("<Button-1>", lambda e: setattr(self, "current_tree", tree))

        def on_selection_change(event):
            setattr(self, "current_tree", tree)
            selected = tree.selection()
            if selected and on_select_callback:
                row_id = selected[0]
                if (tree, row_id) in self.global_map:
                    _, _, item = self.global_map[(tree, row_id)]
                    on_select_callback(item, tree, row_id)

        tree.bind("<<TreeviewSelect>>", on_selection_change)

        def populate_tree_rows(query=""):
            for item_id in tree.get_children():
                tree.delete(item_id)

            query = query.strip().lower()
            visible_count = 0

            for index, item in enumerate(data):
                values = []
                for col in columns:
                    if col == "name":
                        raw_n = item.get("name", "")
                        values.append(get_display_name(raw_n))
                    elif col == "stacks":
                        if "stacks" in item:
                            values.append(item["stacks"])
                        elif "unknown" in item and "unknown001" in item.get("unknown", {}):
                            values.append(item["unknown"]["unknown001"])
                        else:
                            values.append("")
                    elif col == "craftPlan":
                        raw_cp = item.get("craftPlan", "")
                        values.append(get_craftplan_display_name(raw_cp))
                    elif col == "upgradeSockets":
                        socks = item.get("upgradeSockets", [])
                        disp_socks = [get_socket_display_name(s) for s in socks if s]
                        values.append(", ".join(disp_socks))
                    else:
                        values.append(item.get(col, ""))

                if query:
                    matches = any(query in str(v).lower() for v in values)
                    if not matches:
                        continue

                row_id = tree.insert("", tk.END, values=values)
                map_ref[row_id] = (tree, index, data)
                self.global_map[(tree, row_id)] = (index, data, item)
                visible_count += 1

            count_label.config(text=f"{visible_count} of {len(data)} items")

        populate_tree_rows()

        def on_search_change(*args):
            if debounce_timer[0] is not None:
                self.after_cancel(debounce_timer[0])
            debounce_timer[0] = self.after(180, lambda: populate_tree_rows(search_var.get()))

        search_var.trace_add("write", on_search_change)

        tree.bind("<Double-1>", lambda e: self.edit_cell(e, tree, columns))

        def on_drag_select(event):
            row = tree.identify_row(event.y)
            if row:
                tree.selection_add(row)

        tree.bind("<B1-Motion>", on_drag_select)

        return tree

    def edit_cell(self, event, tree, columns):
        row_id = tree.identify_row(event.y)
        if not row_id:
            return

        col_id_str = tree.identify_column(event.x)
        if not col_id_str:
            return
        col_index = int(col_id_str[1:]) - 1
        if col_index < 0 or col_index >= len(columns):
            return

        key = columns[col_index]

        bbox = tree.bbox(row_id, f"#{col_index+1}")
        if not bbox:
            return
        x, y, width, height = bbox

        entry = tk.Entry(tree, bg=BG_INPUT, fg=FG_MAIN, insertbackground=FG_MAIN)
        entry.place(x=x, y=y, width=width, height=height)

        # Si editamos 'name', mostramos el nombre técnico real para que no inserte los corchetes
        if (tree, row_id) in self.global_map:
            _, _, item_obj = self.global_map[(tree, row_id)]
            current_value = item_obj.get(key, "")
        else:
            current_value = tree.item(row_id)["values"][col_index]

        entry.insert(0, str(current_value) if current_value is not None else "")
        entry.focus()

        def save_edit(e=None):
            new_value = entry.get().strip()
            if (tree, row_id) not in self.global_map:
                entry.destroy()
                return

            index, parent_list, item = self.global_map[(tree, row_id)]

            try:
                if key == "name":
                    item[key] = new_value

                elif key == "stacks":
                    if "stacks" in item:
                        item["stacks"] = int(new_value)
                    elif "unknown" in item and "unknown001" in item["unknown"]:
                        item["unknown"]["unknown001"] = int(new_value)

                elif key in ["quantity", "repairs", "id"]:
                    item[key] = int(new_value)

                elif key == "condition":
                    item[key] = float(new_value)

                elif key == "craftPlan":
                    item[key] = new_value

                elif key == "upgradeSockets":
                    item["upgradeSockets"] = [s.strip() for s in new_value.split(",") if s.strip()]

                else:
                    item[key] = new_value

                self.refresh_tree_row(tree, row_id, item)
                self.mark_dirty(True)

            except ValueError as ve:
                messagebox.showerror("Invalid Input", f"Value '{new_value}' is not valid for {key}.\nPlease enter a valid number.")
                return
            except Exception as e:
                print("ERROR:", e, "| value:", new_value)
                return

            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)
        entry.bind("<Escape>", lambda e: entry.destroy())

    # ==================== STATS TAB ====================
    def create_stats(self, parent, player):
        inv = player.setdefault("inventory", {})

        stats_container = tk.LabelFrame(parent, text="Player Attributes & Currency", bg=BG_MAIN, fg=ACCENT_ORANGE, font=("Segoe UI", 10, "bold"), padx=20, pady=15)
        stats_container.pack(fill=tk.X, padx=15, pady=15)

        # Health
        f_health = tk.Frame(stats_container, bg=BG_MAIN)
        f_health.pack(fill=tk.X, pady=8)
        tk.Label(f_health, text="Health", width=14, anchor="w", bg=BG_MAIN, fg=FG_MAIN, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        health_var = tk.StringVar(value=str(player.get("health", 100.0)))
        entry_h = ttk.Entry(f_health, textvariable=health_var, width=20)
        entry_h.pack(side=tk.LEFT, padx=6)

        def save_health(e=None):
            try:
                player["health"] = float(health_var.get())
                self.mark_dirty(True)
            except ValueError:
                pass
        entry_h.bind("<Return>", save_health)
        entry_h.bind("<FocusOut>", save_health)
        ttk.Button(f_health, text="Max (9999)", command=lambda: [health_var.set("9999"), save_health()]).pack(side=tk.LEFT, padx=6)

        # Fury
        f_fury = tk.Frame(stats_container, bg=BG_MAIN)
        f_fury.pack(fill=tk.X, pady=8)
        tk.Label(f_fury, text="Fury", width=14, anchor="w", bg=BG_MAIN, fg=FG_MAIN, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        fury_var = tk.StringVar(value=str(player.get("fury", 0.0)))
        entry_f = ttk.Entry(f_fury, textvariable=fury_var, width=20)
        entry_f.pack(side=tk.LEFT, padx=6)

        def save_fury(e=None):
            try:
                player["fury"] = float(fury_var.get())
                self.mark_dirty(True)
            except ValueError:
                pass
        entry_f.bind("<Return>", save_fury)
        entry_f.bind("<FocusOut>", save_fury)
        ttk.Button(f_fury, text="Max (9999)", command=lambda: [fury_var.set("9999"), save_fury()]).pack(side=tk.LEFT, padx=6)

        # Money / Cash
        f_cash = tk.Frame(stats_container, bg=BG_MAIN)
        f_cash.pack(fill=tk.X, pady=8)
        tk.Label(f_cash, text="Money (Cash)", width=14, anchor="w", bg=BG_MAIN, fg=FG_MAIN, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        cash_var = tk.StringVar(value=str(inv.get("cash", 0)))
        entry_c = ttk.Entry(f_cash, textvariable=cash_var, width=20)
        entry_c.pack(side=tk.LEFT, padx=6)

        def save_cash(e=None):
            try:
                inv["cash"] = int(cash_var.get())
                self.mark_dirty(True)
            except ValueError:
                pass
        entry_c.bind("<Return>", save_cash)
        entry_c.bind("<FocusOut>", save_cash)
        ttk.Button(f_cash, text="Max (999,999,999)", command=lambda: [cash_var.set("999999999"), save_cash()]).pack(side=tk.LEFT, padx=6)

    # ==================== OPERACIONES Y TRUCOS ====================
    def copy_row(self, tree):
        selected = tree.selection()
        if not selected:
            return

        row_id = selected[0]
        if (tree, row_id) in self.global_map:
            index, parent_list, item = self.global_map[(tree, row_id)]
            self.clipboard_data = copy.deepcopy(item)
            disp = get_display_name(item.get("name", "selected"))
            self.set_status(f"Copied item: {disp}")

    def paste_row(self, tree):
        selected = tree.selection()
        if not selected or not self.clipboard_data:
            return

        row_id = selected[0]
        if (tree, row_id) in self.global_map:
            index, parent_list, target = self.global_map[(tree, row_id)]
            for key, val in self.clipboard_data.items():
                target[key] = copy.deepcopy(val)

            self.refresh_tree_row(tree, row_id, target)
            self.mark_dirty(True)
            self.set_status("Pasted item data")

    def duplicate_row(self, tree):
        selected = tree.selection()
        if not selected or not self.current_data:
            return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})
        storage = player.get("storage", {})

        json_lists = [
            inventory.get("items1"),
            inventory.get("quickSlots"),
            inventory.get("equipmentSlots"),
            inventory.get("items3"),
            storage.get("items1"),
            storage.get("items3")
        ]

        for row_id in selected:
            if (tree, row_id) not in self.global_map:
                continue

            index, data, item = self.global_map[(tree, row_id)]
            new_item = copy.deepcopy(item)

            if "id" in new_item and isinstance(new_item["id"], int):
                new_item["id"] += 1000000

            appended = False
            for target_list in json_lists:
                if isinstance(target_list, list) and item in target_list:
                    pos = target_list.index(item)
                    target_list.insert(pos + 1, new_item)
                    appended = True
                    break

            if not appended:
                data.append(new_item)

        self.mark_dirty(True)
        self.populate()

    def show_about(self):
        win = tk.Toplevel(self)
        win.title("About")
        win.geometry("420x240")
        win.configure(bg=BG_MAIN)
        win.transient(self)

        tk.Label(win, text="Dying Light Save Editor GUI 1.6", bg=BG_MAIN, fg=ACCENT_ORANGE, font=("Segoe UI", 14, "bold")).pack(pady=(20, 5))
        tk.Label(win, text="By EllisGamingTv", bg=BG_MAIN, fg=FG_MAIN, font=("Segoe UI", 11)).pack(pady=(0, 10))

        tk.Label(
            win,
            text="A powerful GUI editor for Dying Light save files.\nRequires Steffen's CLI to decrypt and encrypt save files.",
            bg=BG_MAIN,
            fg=FG_MUTED,
            wraplength=360,
            justify="center",
            font=("Segoe UI", 9)
        ).pack(pady=5)

        link = tk.Label(win, text="Download Steffen's CLI here", bg=BG_MAIN, fg=ACCENT_BLUE, cursor="hand2", font=("Segoe UI", 9, "underline"))
        link.pack(pady=12)

        def open_link(e):
            webbrowser.open("https://steffenl.com/projects/dying-light-save-editor/releases")

        link.bind("<Button-1>", open_link)

    def cleanup(self):
        for p in (TEMP_JSON, TEMP_SAVE):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

    def on_close(self):
        if not self.check_unsaved_changes():
            return
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr
        self.cleanup()
        self.destroy()

    def max_kings(self):
        if not self.current_data:
            return

        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            return

        for row_id in selected:
            if (tree, row_id) in self.global_map:
                index, parent_list, item = self.global_map[(tree, row_id)]
                max_kings(item)

        self.mark_dirty(True)
        self.populate()

    def max_amount(self):
        if not self.current_data:
            return

        tree = self.current_tree
        selected = tree.selection() if tree else []

        if selected:
            for row_id in selected:
                if (tree, row_id) not in self.global_map:
                    continue
                index, parent_list, item = self.global_map[(tree, row_id)]
                if "quantity" in item:
                    max_quantity(item)
                elif "stacks" in item:
                    max_skill(item)
                elif "unknown" in item and "unknown001" in item["unknown"]:
                    item["unknown"]["unknown001"] = 9999
        else:
            player = self.current_data.get("player", {})
            inv = player.get("inventory", {})

            for obj in inv.get("equipmentSlots", []):
                if isinstance(obj, dict) and "quantity" in obj:
                    obj["quantity"] = 999999999

            for obj in inv.get("items3", []):
                if isinstance(obj, dict) and "quantity" in obj:
                    obj["quantity"] = 999999999

            for skill in player.get("skills", []):
                if isinstance(skill, dict) and "stacks" in skill:
                    skill["stacks"] = 9999

            for buff in player.get("buffs", []):
                if isinstance(buff, dict):
                    if "stacks" in buff:
                        buff["stacks"] = 9999
                    elif "unknown" in buff and "unknown001" in buff.get("unknown", {}):
                        buff["unknown"]["unknown001"] = 9999

        self.mark_dirty(True)
        self.populate()

    def run_plugin(self, plugin):
        print(f"[APP] Running plugin: {plugin.get('name')}")
        try:
            items = []
            tree = self.current_tree
            if tree:
                for row_id in tree.selection():
                    if (tree, row_id) in self.global_map:
                        _, _, item = self.global_map[(tree, row_id)]
                        items.append(item)

            if plugin.get("run"):
                plugin["run"](self, items)

            print("[APP] Plugin finished successfully")
            self.mark_dirty(True)
        except Exception as e:
            import traceback
            print("[PLUGIN ERROR]")
            traceback.print_exc()

        self.populate()

    def add_legend_skills(self):
        if not self.current_data:
            return

        player = self.current_data.setdefault("player", {})
        buffs = player.setdefault("buffs", [])

        existing = {b.get("name") for b in buffs if isinstance(b, dict)}

        for skill in LEGEND_SKILLS:
            skill_name = skill + "_skill"
            if skill_name not in existing:
                buffs.append({
                    "name": skill_name,
                    "stacks": 25
                })

        self.mark_dirty(True)
        self.populate()

    def delete_selected_skills(self):
        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            return

        player = self.current_data.get("player", {})

        for row_id in reversed(selected):
            if (tree, row_id) not in self.global_map:
                continue

            index, data, item = self.global_map[(tree, row_id)]

            if item in player.get("buffs", []):
                player["buffs"].remove(item)
            elif item in player.get("skills", []):
                player["skills"].remove(item)

        self.mark_dirty(True)
        self.populate()

    def max_weapon_stats(self):
        if not self.current_data:
            return

        tree = self.current_tree
        selected = tree.selection() if tree else []

        if selected:
            for row_id in selected:
                if (tree, row_id) not in self.global_map:
                    continue
                index, parent_list, item = self.global_map[(tree, row_id)]
                if isinstance(item, dict):
                    if "condition" in item:
                        item["condition"] = 999999.0
                    if "repairs" in item:
                        item["repairs"] = 0
        else:
            player = self.current_data.get("player", {})
            inventory = player.get("inventory", {})

            for item in inventory.get("equipmentSlots", []):
                if isinstance(item, dict):
                    if "condition" in item:
                        item["condition"] = 999999.0
                    if "repairs" in item:
                        item["repairs"] = 0

            for item in inventory.get("items3", []):
                if isinstance(item, dict):
                    if "condition" in item:
                        item["condition"] = 999999.0
                    if "repairs" in item:
                        item["repairs"] = 0

        self.mark_dirty(True)
        self.populate()

    def apply_rarity(self):
        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            return

        rarity = self.rarity_var.get()
        for row_id in selected:
            if (tree, row_id) not in self.global_map:
                continue
            _, _, item = self.global_map[(tree, row_id)]
            set_rarity(item, rarity)

        self.mark_dirty(True)
        self.populate()

    def set_all_platinum(self):
        if not self.current_data:
            return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", [])
        )

        for item in all_items:
            if isinstance(item, dict):
                set_platinum(item)

        self.mark_dirty(True)
        self.populate()

    def edit_sockets_window(self):
        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            return

        row_id = selected[0]
        if (tree, row_id) not in self.global_map:
            return
        _, _, item = self.global_map[(tree, row_id)]

        if "upgradeSockets" not in item or not isinstance(item["upgradeSockets"], list):
            item["upgradeSockets"] = []

        win = tk.Toplevel(self)
        win.title("Edit Sockets")
        win.geometry("420x520")
        win.configure(bg=BG_MAIN)
        win.transient(self)

        socket_vars = []

        scroll_container = tk.Frame(win, bg=BG_MAIN)
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        canvas = tk.Canvas(scroll_container, bg=BG_MAIN, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas, bg=BG_MAIN)

        inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def add_socket(value=""):
            if len(socket_vars) >= 20:
                return
            var = tk.StringVar(value=value if value else self.socket_options[0])
            combo = ttk.Combobox(
                inner_frame,
                textvariable=var,
                values=self.socket_options,
                state="readonly",
                width=35
            )
            combo.pack(pady=4)
            socket_vars.append(var)

        for socket in item["upgradeSockets"]:
            add_socket(socket)

        def save_sockets():
            item["upgradeSockets"] = [var.get() for var in socket_vars if var.get()]
            self.mark_dirty(True)
            win.destroy()
            self.populate()

        btn_box = tk.Frame(win, bg=BG_MAIN)
        btn_box.pack(fill=tk.X, pady=10, padx=12)
        ttk.Button(btn_box, text="+ Add Socket", command=add_socket).pack(side=tk.LEFT)
        ttk.Button(btn_box, text="Save Sockets", style="Accent.TButton", command=save_sockets).pack(side=tk.RIGHT)

    def check_ids(self):
        if not self.current_data:
            messagebox.showinfo("Check IDs", "No save file loaded.")
            return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", []) +
            inventory.get("items3", [])
        )

        duplicates = get_duplicate_id_map(all_items)

        if not duplicates:
            messagebox.showinfo("Check IDs", "No duplicate IDs found.")
            return

        msg = ""
        for item_id, items in duplicates.items():
            msg += f"ID {item_id} -> {len(items)} items\n"

        messagebox.showwarning("Duplicate IDs Found", msg)

    def set_unknown008(self):
        if not self.current_data:
            return

        def apply(item):
            if isinstance(item, dict):
                if "unknown" not in item or not isinstance(item["unknown"], dict):
                    item["unknown"] = {}
                item["unknown"]["unknown008"] = 8

        tree = self.current_tree
        if tree:
            selected = tree.selection()
            if selected:
                for row_id in selected:
                    if (tree, row_id) in self.global_map:
                        _, _, item = self.global_map[(tree, row_id)]
                        apply(item)
                self.mark_dirty(True)
                self.populate()
                return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})
        storage = player.get("storage", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", []) +
            inventory.get("items3", []) +
            storage.get("items1", []) +
            storage.get("items3", [])
        )

        for item in all_items:
            apply(item)

        self.mark_dirty(True)
        self.populate()

    def set_op_craft_combo(self):
        if not self.current_data:
            return

        def apply(item):
            if not isinstance(item, dict):
                return
            item["craftPlan"] = "Craftplan_GTFO20"
            item["upgradeSockets"] = [
                "Craftplan_GTFO20",
                "Craftplan_LightingRod",
                "Throwable_PoisonGrenade",
                "Craft_Upgrade_DamL2DurL2BalL2"
            ]

        tree = self.current_tree
        if tree:
            selected = tree.selection()
            if selected:
                for row_id in selected:
                    if (tree, row_id) in self.global_map:
                        _, _, item = self.global_map[(tree, row_id)]
                        apply(item)
                self.mark_dirty(True)
                self.populate()
                return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", [])
        )

        for item in all_items:
            apply(item)

        self.mark_dirty(True)
        self.populate()

    def apply_craftplan(self):
        if not self.current_data:
            return

        craftplan = self.craftplan_var.get()

        def apply(item):
            if isinstance(item, dict):
                item["craftPlan"] = craftplan

        tree = self.current_tree
        if tree and tree.selection():
            for row_id in tree.selection():
                if (tree, row_id) in self.global_map:
                    _, _, item = self.global_map[(tree, row_id)]
                    apply(item)
            self.mark_dirty(True)
            self.populate()
            return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", [])
        )

        for item in all_items:
            apply(item)

        self.mark_dirty(True)
        self.populate()

    def apply_weapon_name(self):
        if not self.current_data:
            return

        new_name = self.weapon_name_var.get()

        def apply(item):
            if isinstance(item, dict) and "name" in item:
                item["name"] = new_name

        tree = self.current_tree
        if tree and tree.selection():
            for row_id in tree.selection():
                if (tree, row_id) in self.global_map:
                    _, _, item = self.global_map[(tree, row_id)]
                    apply(item)
            self.mark_dirty(True)
            self.populate()
            return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", [])
        )

        for item in all_items:
            apply(item)

        self.mark_dirty(True)
        self.populate()

    def add_collectibles(self):
        if not self.current_data:
            return

        player = self.current_data.setdefault("player", {})
        inventory = player.setdefault("inventory", {})
        items3 = inventory.setdefault("items3", [])

        existing_names = {item.get("name") for item in items3 if isinstance(item, dict)}

        for i, name in enumerate(COLLECTIBLES):
            if name in existing_names:
                continue

            items3.append({
                "id": 8000000 + i,
                "name": name,
                "quantity": 1
            })

        self.mark_dirty(True)
        self.populate()

    def toggle_console(self):
        if self.console_visible:
            self.console.pack_forget()
            self.console_visible = False
        else:
            self.console.pack(fill=tk.X, padx=8, pady=4)
            self.console_visible = True
            self.console.insert("end",
                "[INFO] Debug console enabled.\n"
                "Plugins output and internal logs appear here.\n\n"
            )
            self.console.see("end")

    def add_special_skill(self):
        if not self.current_data:
            return

        player = self.current_data.setdefault("player", {})
        buffs = player.setdefault("buffs", [])

        skill_name = self.special_skill_var.get()
        full_name = skill_name + "_skill"

        existing = {b.get("name") for b in buffs if isinstance(b, dict)}

        if full_name not in existing:
            buffs.append({
                "name": full_name,
                "stacks": 1
            })

        self.mark_dirty(True)
        self.populate()


class ConsoleRedirect:
    def __init__(self, textbox, orig_stream=None):
        self.textbox = textbox
        self.orig_stream = orig_stream

    def write(self, text):
        if self.orig_stream:
            try:
                self.orig_stream.write(text)
                self.orig_stream.flush()
            except Exception:
                pass
        try:
            self.textbox.after(0, self._write, text)
        except Exception:
            pass

    def _write(self, text):
        try:
            self.textbox.insert("end", text)
            self.textbox.see("end")
        except Exception:
            pass

    def flush(self):
        if self.orig_stream:
            try:
                self.orig_stream.flush()
            except Exception:
                pass
