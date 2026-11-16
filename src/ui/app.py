import tkinter as tk
from ui.common import *
from ui.save_io import SaveIOMixin
from ui.dialogs import DialogsMixin
from ui.tables import TablesMixin
from ui.actions import ActionsMixin


class SaveEditorApp(SaveIOMixin, DialogsMixin, TablesMixin, ActionsMixin, tk.Tk):
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
        self.plugins = load_plugins(confirm=self._confirm_plugin, trusted=self.config_data.setdefault('trusted_plugins', {}))
        save_config(self.config_data)
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
    def on_close(self):
        if not self.check_unsaved_changes():
            return
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr
        self.cleanup()
        self.destroy()

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
