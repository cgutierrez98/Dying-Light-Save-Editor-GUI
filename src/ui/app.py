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
        self.geometry("1060x720")
        self.minsize(920, 600)

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

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        check_updates_async(self)
        for plugin in self.plugins:
            if plugin.get("init_ui"):
                try:
                    plugin["init_ui"](self)
                except Exception as e:
                    print(f"[PLUGIN INIT ERROR] {plugin.get('name')}: {e}")

    def create_widgets(self):
        # Barra superior fila 1: Archivo y Utilidades
        top_bar1 = tk.Frame(self)
        top_bar1.pack(fill=tk.X, padx=5, pady=(5, 2))

        tk.Button(top_bar1, text="Open Save", command=self.load_save).pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar1, text="Save Changes", command=self.save_changes, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar1, text="Backups / Restore", command=self.show_backups_window).pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar1, text="Select CLI", command=self.select_editor_cli).pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar1, text="Check IDs", command=self.check_ids).pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar1, text="Toggle Console", command=self.toggle_console).pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar1, text="About", command=self.show_about).pack(side=tk.LEFT, padx=3)

        self.status = tk.Label(top_bar1, text="", font=("Arial", 9, "italic"), fg="#0055aa")
        self.status.pack(side=tk.RIGHT, padx=10)

        # Barra superior fila 2: Trucos y Modificadores Rápidos
        top_bar2 = tk.Frame(self)
        top_bar2.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Button(top_bar2, text="Full Kings", command=self.max_kings).pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar2, text="Max Amount", command=self.max_amount).pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar2, text="Edit Sockets", command=self.edit_sockets_window).pack(side=tk.LEFT, padx=3)

        # Rarity
        self.rarity_var = tk.StringVar(value="white")
        rarity_menu = ttk.Combobox(
            top_bar2,
            textvariable=self.rarity_var,
            values=["white", "green", "blue", "violet", "orange", "platinum"],
            state="readonly",
            width=9
        )
        rarity_menu.pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar2, text="Apply Rarity", command=self.apply_rarity).pack(side=tk.LEFT, padx=2)

        # Craftplan
        self.craftplan_var = tk.StringVar(value=ORANGE_CRAFTPLANS[0])
        craftplan_menu = ttk.Combobox(
            top_bar2,
            textvariable=self.craftplan_var,
            values=ORANGE_CRAFTPLANS,
            state="readonly",
            width=20
        )
        craftplan_menu.pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar2, text="Apply Craftplan", command=self.apply_craftplan).pack(side=tk.LEFT, padx=2)

        # Weapon Name
        self.weapon_name_var = tk.StringVar(value=WEAPON_NAMES[0])
        weapon_menu = ttk.Combobox(
            top_bar2,
            textvariable=self.weapon_name_var,
            values=WEAPON_NAMES,
            state="readonly",
            width=20
        )
        weapon_menu.pack(side=tk.LEFT, padx=3)
        tk.Button(top_bar2, text="Apply Weapon Name", command=self.apply_weapon_name).pack(side=tk.LEFT, padx=2)

        # Notebook (Pestañas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        self.tab_weapons = ttk.Frame(self.notebook)
        self.tab_inventory = ttk.Frame(self.notebook)
        self.tab_skills = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)
        self.tab_stash = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_weapons, text="Weapons")
        self.notebook.add(self.tab_inventory, text="Inventory")
        self.notebook.add(self.tab_skills, text="Skills")
        self.notebook.add(self.tab_stats, text="Stats")
        self.notebook.add(self.tab_stash, text="Stash")

        def on_tab_changed(event):
            selected_tab = self.notebook.select()
            if selected_tab == str(self.tab_weapons):
                if self.weapon_tree:
                    self.current_tree = self.weapon_tree
            elif selected_tab == str(self.tab_inventory):
                if self.inventory_tree:
                    self.current_tree = self.inventory_tree
            elif selected_tab == str(self.tab_skills):
                if self.skills_tree:
                    self.current_tree = self.skills_tree
            elif selected_tab == str(self.tab_stash):
                if self.stash_tree:
                    self.current_tree = self.stash_tree

        self.notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

        # Plugins Frame
        if self.plugins:
            plugin_frame = tk.LabelFrame(self, text="Plugins")
            plugin_frame.pack(fill=tk.X, padx=5, pady=3)
            for plugin in self.plugins:
                tk.Button(
                    plugin_frame,
                    text=plugin["name"],
                    command=lambda p=plugin: self.run_plugin(p)
                ).pack(side=tk.LEFT, padx=4, pady=2)

        # Debug Console
        self.console = tk.Text(self, height=10, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 9))
        sys.stdout = ConsoleRedirect(self.console, self._orig_stdout)
        sys.stderr = ConsoleRedirect(self.console, self._orig_stderr)

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            self.json_path = path

    def set_status(self, text):
        self.status.config(text=text)
        self.update_idletasks()

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
            return subprocess.run(
                [editor_exe, *args],
                cwd=cwd
            )
        except Exception as e:
            messagebox.showerror("Error ejecutando editor.exe", str(e))
            return None

    def load_save(self, ask_file=True):
        if ask_file or not self.save_path:
            initial_dir = os.path.dirname(self.save_path) if self.save_path else (EDITOR_DIR if os.path.exists(EDITOR_DIR) else None)
            path = filedialog.askopenfilename(
                title="Select Dying Light Save File",
                initialdir=initial_dir,
                filetypes=[("Dying Light Save", "*.sav"), ("All files", "*.*")]
            )
            if not path:
                return
            self.save_path = path

        if not self.save_path or not os.path.exists(self.save_path):
            messagebox.showerror("Error", "No valid .sav file selected.")
            return

        self.config_data["last_save_path"] = self.save_path
        save_config(self.config_data)

        self.set_status("Decrypting save...")

        ret = self._run_editor([
            "sample",
            self.save_path,
            f"--patch={TEMP_JSON}"
        ])

        if ret is None:
            self.set_status("")
            return

        if os.path.exists(TEMP_JSON):
            with open(TEMP_JSON, "r", encoding="utf-8") as f:
                self.current_data = json.load(f)
            self.populate()
            self.title(f"Dying Light Save Editor GUI 1.6 - {os.path.basename(self.save_path)}")
        else:
            messagebox.showerror("Error", "Could not decrypt the selected .sav file.\nMake sure editor.exe is the CLI by Steffen.")

        self.set_status("")

    def save_changes(self):
        if not self.current_data or not self.save_path:
            messagebox.showwarning("Warning", "No save loaded to save changes.")
            return
        self.focus()

        self.set_status("Creating automatic backup...")
        backup_file = create_save_backup(self.save_path)

        self.set_status("Saving changes...")

        try:
            with open(TEMP_JSON, "w", encoding="utf-8") as f:
                json.dump(self.current_data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write temporary JSON:\n{e}")
            self.set_status("")
            return

        time.sleep(0.1)

        ret = self._run_editor([
            "update",
            self.save_path,
            f"--patch={TEMP_JSON}",
            f"--output={TEMP_SAVE}"
        ])

        if ret is None:
            self.set_status("")
            return

        if os.path.exists(TEMP_SAVE):
            try:
                shutil.move(TEMP_SAVE, self.save_path)
                backup_info = f"\n\nAutomatic backup created:\n{os.path.basename(backup_file)}" if backup_file else ""
                messagebox.showinfo("Saved", f"Changes successfully saved to {os.path.basename(self.save_path)}!{backup_info}")
                self.load_save(ask_file=False)
            except Exception as e:
                messagebox.showerror("Error", f"Could not overwrite save file:\n{e}")
        else:
            messagebox.showerror("Error", "Could not update the .sav file with Steffen's CLI.")

        self.cleanup()
        self.set_status("")

    def show_backups_window(self):
        if not self.save_path:
            messagebox.showinfo("Backups", "Open a save file first to view its backups.")
            return

        backups = list_save_backups(self.save_path)
        win = tk.Toplevel(self)
        win.title(f"Backups - {os.path.basename(self.save_path)}")
        win.geometry("600x380")
        win.transient(self)

        tk.Label(win, text=f"Available Backups for: {os.path.basename(self.save_path)}", font=("Arial", 10, "bold")).pack(pady=8)

        if not backups:
            tk.Label(win, text="No automatic backups found for this save file yet.\nBackups are created automatically every time you click 'Save Changes'.", fg="gray").pack(pady=30)
            tk.Button(win, text="Close", command=win.destroy).pack(pady=10)
            return

        list_frame = tk.Frame(win)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        lb = tk.Listbox(list_frame, font=("Consolas", 9))
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=sb.set)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        for b in backups:
            mtime = datetime.fromtimestamp(os.path.getmtime(b)).strftime("%Y-%m-%d %H:%M:%S")
            size_kb = os.path.getsize(b) / 1024
            lb.insert(tk.END, f"{os.path.basename(b)}  ({mtime}, {size_kb:.1f} KB)")
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

        btn_box = tk.Frame(win)
        btn_box.pack(fill=tk.X, pady=10)
        tk.Button(btn_box, text="Restore Selected Backup", command=restore_selected, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=15)
        tk.Button(btn_box, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=15)

    def populate(self):
        for tab in (self.tab_weapons, self.tab_inventory, self.tab_skills, self.tab_stats, self.tab_stash):
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

        # ==================== WEAPONS TAB ====================
        weapon_actions_frame = tk.Frame(self.tab_weapons)
        weapon_actions_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(weapon_actions_frame, text="Powerful Weapon", command=self.set_unknown008).pack(side=tk.LEFT, padx=4)
        tk.Button(weapon_actions_frame, text="Max Condition + Reset Repairs", command=self.max_weapon_stats).pack(side=tk.LEFT, padx=4)
        tk.Button(weapon_actions_frame, text="All Platinum", command=self.set_all_platinum).pack(side=tk.LEFT, padx=4)
        tk.Button(weapon_actions_frame, text="OP Craft Combo", command=self.set_op_craft_combo).pack(side=tk.LEFT, padx=4)

        self.weapon_tree = self.create_table(
            self.tab_weapons,
            ["name", "quantity", "condition", "repairs", "id", "craftPlan", "upgradeSockets"],
            weapons,
            self.weapon_map
        )

        # ==================== INVENTORY TAB ====================
        inv_actions_frame = tk.Frame(self.tab_inventory)
        inv_actions_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(inv_actions_frame, text="All Platinum", command=self.set_all_platinum).pack(side=tk.LEFT, padx=4)
        tk.Button(inv_actions_frame, text="Powerful Weapon", command=self.set_unknown008).pack(side=tk.LEFT, padx=4)
        tk.Button(inv_actions_frame, text="Add Collectibles", command=self.add_collectibles).pack(side=tk.LEFT, padx=4)

        self.inventory_tree = self.create_table(
            self.tab_inventory,
            ["name", "quantity", "id", "craftPlan", "upgradeSockets"],
            items,
            self.inventory_map
        )

        # ==================== SKILLS TAB ====================
        skills_actions_frame = tk.Frame(self.tab_skills)
        skills_actions_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(skills_actions_frame, text="Add All Legend Skills", command=self.add_legend_skills).pack(side=tk.LEFT, padx=4)

        self.special_skill_var = tk.StringVar(value="ZombieSprintUpgrade")
        skill_dropdown = ttk.Combobox(
            skills_actions_frame,
            textvariable=self.special_skill_var,
            values=["ZombieSprintUpgrade", "ZombieRopeLocoUpgrade"],
            state="readonly",
            width=25
        )
        skill_dropdown.pack(side=tk.LEFT, padx=4)

        tk.Button(skills_actions_frame, text="Add Skill", command=self.add_special_skill).pack(side=tk.LEFT, padx=4)
        tk.Button(skills_actions_frame, text="Delete Selected", command=self.delete_selected_skills).pack(side=tk.LEFT, padx=4)

        skills_container = tk.Frame(self.tab_skills)
        skills_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.skills_tree = ttk.Treeview(skills_container, columns=("name", "stacks"), show="headings", selectmode="extended")
        self.skills_tree.heading("name", text="Name")
        self.skills_tree.heading("stacks", text="Stacks")

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

            item_id = self.skills_tree.insert("", "end", values=(
                name.replace("_skill", "").replace("_", " "),
                buff.get("stacks", 0)
            ))
            self.skill_map[item_id] = buff
            self.global_map[(self.skills_tree, item_id)] = (None, None, buff)

        # ==================== STATS TAB ====================
        self.create_stats(self.tab_stats, player)

        # ==================== STASH TAB ====================
        stash_actions_frame = tk.Frame(self.tab_stash)
        stash_actions_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(stash_actions_frame, text="All Platinum", command=self.set_all_platinum).pack(side=tk.LEFT, padx=4)
        tk.Button(stash_actions_frame, text="Powerful Weapon", command=self.set_unknown008).pack(side=tk.LEFT, padx=4)
        tk.Button(stash_actions_frame, text="OP Craft Combo", command=self.set_op_craft_combo).pack(side=tk.LEFT, padx=4)

        self.stash_tree = self.create_table(
            self.tab_stash,
            ["name", "quantity", "id", "craftPlan", "upgradeSockets"],
            stash_items,
            self.inventory_map
        )

        # Actualizar árbol activo según la pestaña visible
        selected_tab = self.notebook.select() if hasattr(self, "notebook") else None
        if selected_tab == str(self.tab_inventory):
            self.current_tree = self.inventory_tree
        elif selected_tab == str(self.tab_skills):
            self.current_tree = self.skills_tree
        elif selected_tab == str(self.tab_stash):
            self.current_tree = self.stash_tree
        else:
            self.current_tree = self.weapon_tree

    def create_stats(self, parent, player):
        inv = player.setdefault("inventory", {})

        stats_container = tk.LabelFrame(parent, text="Player Attributes & Currency", padx=15, pady=15)
        stats_container.pack(fill=tk.X, padx=15, pady=10)

        # Health
        f_health = tk.Frame(stats_container)
        f_health.pack(fill=tk.X, pady=6)
        tk.Label(f_health, text="Health", width=12, anchor="w", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        health_var = tk.StringVar(value=str(player.get("health", 100.0)))
        entry_h = tk.Entry(f_health, textvariable=health_var, width=20)
        entry_h.pack(side=tk.LEFT, padx=5)

        def save_health(e=None):
            try:
                player["health"] = float(health_var.get())
            except ValueError:
                pass
        entry_h.bind("<Return>", save_health)
        entry_h.bind("<FocusOut>", save_health)
        tk.Button(f_health, text="Max", command=lambda: [health_var.set("9999"), save_health()]).pack(side=tk.LEFT, padx=5)

        # Fury
        f_fury = tk.Frame(stats_container)
        f_fury.pack(fill=tk.X, pady=6)
        tk.Label(f_fury, text="Fury", width=12, anchor="w", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        fury_var = tk.StringVar(value=str(player.get("fury", 0.0)))
        entry_f = tk.Entry(f_fury, textvariable=fury_var, width=20)
        entry_f.pack(side=tk.LEFT, padx=5)

        def save_fury(e=None):
            try:
                player["fury"] = float(fury_var.get())
            except ValueError:
                pass
        entry_f.bind("<Return>", save_fury)
        entry_f.bind("<FocusOut>", save_fury)
        tk.Button(f_fury, text="Max", command=lambda: [fury_var.set("9999"), save_fury()]).pack(side=tk.LEFT, padx=5)

        # Money / Cash
        f_cash = tk.Frame(stats_container)
        f_cash.pack(fill=tk.X, pady=6)
        tk.Label(f_cash, text="Money (Cash)", width=12, anchor="w", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        cash_var = tk.StringVar(value=str(inv.get("cash", 0)))
        entry_c = tk.Entry(f_cash, textvariable=cash_var, width=20)
        entry_c.pack(side=tk.LEFT, padx=5)

        def save_cash(e=None):
            try:
                inv["cash"] = int(cash_var.get())
            except ValueError:
                pass
        entry_c.bind("<Return>", save_cash)
        entry_c.bind("<FocusOut>", save_cash)
        tk.Button(f_cash, text="Max", command=lambda: [cash_var.set("999999999"), save_cash()]).pack(side=tk.LEFT, padx=5)

    def create_table(self, parent, columns, data, map_ref):
        container = tk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # Buscador y filtro en tiempo real
        search_frame = tk.Frame(container)
        search_frame.pack(fill=tk.X, pady=(0, 4))

        tk.Label(search_frame, text="Filter:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(2, 4))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=28)
        search_entry.pack(side=tk.LEFT, padx=2)

        clear_btn = ttk.Button(search_frame, text="Clear", command=lambda: search_var.set(""))
        clear_btn.pack(side=tk.LEFT, padx=4)

        count_label = tk.Label(search_frame, text=f"{len(data)} items", fg="#555555", font=("Arial", 9))
        count_label.pack(side=tk.RIGHT, padx=5)

        # Contenedor de la tabla con Scrollbars
        table_frame = tk.Frame(container)
        table_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        self.tree = tree

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140, minwidth=70)

        # Menú contextual (Clic Derecho)
        menu = tk.Menu(tree, tearoff=0)
        menu.add_command(label="Copy", command=lambda: self.copy_row(tree))
        menu.add_command(label="Paste", command=lambda: self.paste_row(tree))
        menu.add_command(label="Duplicate", command=lambda: self.duplicate_row(tree))

        def show_menu(event):
            row = tree.identify_row(event.y)
            if row:
                if row not in tree.selection():
                    tree.selection_set(row)
                menu.post(event.x_root, event.y_root)

        tree.bind("<Button-3>", show_menu)
        tree.bind("<Button-1>", lambda e: setattr(self, "current_tree", tree))

        def populate_tree_rows(query=""):
            for item_id in tree.get_children():
                tree.delete(item_id)

            query = query.strip().lower()
            visible_count = 0

            for index, item in enumerate(data):
                values = []
                for col in columns:
                    if col == "stacks":
                        if "stacks" in item:
                            values.append(item["stacks"])
                        elif "unknown" in item and "unknown001" in item.get("unknown", {}):
                            values.append(item["unknown"]["unknown001"])
                        else:
                            values.append("")
                    elif col == "upgradeSockets":
                        values.append(",".join(item.get("upgradeSockets", [])))
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
            populate_tree_rows(search_var.get())

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

        entry = tk.Entry(tree)
        entry.place(x=x, y=y, width=width, height=height)

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

                values = list(tree.item(row_id)["values"])
                values[col_index] = new_value
                tree.item(row_id, values=values)

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

    def copy_row(self, tree):
        selected = tree.selection()
        if not selected:
            return

        row_id = selected[0]
        if (tree, row_id) in self.global_map:
            index, parent_list, item = self.global_map[(tree, row_id)]
            self.clipboard_data = copy.deepcopy(item)
            self.set_status(f"Copied item: {item.get('name', 'selected')}")

    def paste_row(self, tree):
        selected = tree.selection()
        if not selected or not self.clipboard_data:
            return

        row_id = selected[0]
        if (tree, row_id) in self.global_map:
            index, parent_list, target = self.global_map[(tree, row_id)]
            for key, val in self.clipboard_data.items():
                target[key] = copy.deepcopy(val)

            columns = tree["columns"]
            values = []
            for col in columns:
                if col == "stacks":
                    if "stacks" in target:
                        values.append(target["stacks"])
                    elif "unknown" in target and "unknown001" in target.get("unknown", {}):
                        values.append(target["unknown"]["unknown001"])
                    else:
                        values.append("")
                elif col == "upgradeSockets":
                    values.append(",".join(target.get("upgradeSockets", [])))
                else:
                    values.append(target.get(col, ""))
            tree.item(row_id, values=values)
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

        self.populate()

    def show_about(self):
        win = tk.Toplevel(self)
        win.title("About")
        win.geometry("420x220")
        win.transient(self)

        tk.Label(win, text="Dying Light Save Editor GUI 1.6", font=("Arial", 14, "bold")).pack(pady=(15, 5))
        tk.Label(win, text="By EllisGamingTv", font=("Arial", 11)).pack(pady=(0, 10))

        tk.Label(
            win,
            text="This tool requires Steffen's Save Editor CLI to decrypt and encrypt save files.",
            wraplength=360,
            justify="center"
        ).pack(pady=5)

        link = tk.Label(win, text="Download Steffen's CLI here", fg="blue", cursor="hand2")
        link.pack(pady=10)

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
        win.geometry("400x500")
        win.transient(self)

        socket_vars = []

        scroll_container = tk.Frame(win)
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(scroll_container)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas)

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
            combo.pack(pady=3)
            socket_vars.append(var)

        for socket in item["upgradeSockets"]:
            add_socket(socket)

        def save_sockets():
            item["upgradeSockets"] = [var.get() for var in socket_vars if var.get()]
            win.destroy()
            self.populate()

        btn_box = tk.Frame(win)
        btn_box.pack(fill=tk.X, pady=8)
        tk.Button(btn_box, text="Add Socket", command=add_socket).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_box, text="Save Sockets", command=save_sockets, font=("Arial", 9, "bold")).pack(side=tk.RIGHT, padx=10)

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

        self.populate()

    def toggle_console(self):
        if self.console_visible:
            self.console.pack_forget()
            self.console_visible = False
        else:
            self.console.pack(fill=tk.X, padx=5, pady=5)
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
