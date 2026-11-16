"""Carga/guardado de saves, CLI de Steffen y backups."""
from ui.common import *


class SaveIOMixin:
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
            "No se encontrÃ³ 'editor.exe' (el CLI de Steffen necesario para desencriptar saves).\n\n"
            "Â¿Deseas buscar y seleccionar 'editor.exe' manualmente?\n\n"
            "(Si no lo tienes, descÃ¡rgalo de https://steffenl.com/projects/dying-light-save-editor/releases)"
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
            self.after(0, lambda err=e: self._on_load_error(f"Error reading save data:\n{err}"))

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
            # 0. Validar datos antes de tocar nada
            validate_save_data(data_snapshot)

            # 1. Backup obligatorio: si falla, se aborta el guardado
            backup_file = create_save_backup(save_path)
            if not backup_file:
                raise RuntimeError("No se pudo crear el backup; guardado cancelado para proteger tu save.")
            prune_backups(save_path)

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
            atomic_replace(TEMP_SAVE, save_path)

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
                    atomic_replace(chosen_backup, self.save_path, keep_source=True)
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
    def _confirm_plugin(self, name, path):
        return messagebox.askyesno(
            "Plugin no verificado",
            f"El plugin '{name}' es nuevo o ha cambiado.\n\n{path}\n\n"
            "Los plugins se ejecutan SIN aislamiento y tienen acceso total a tu equipo.\n"
            "Â¿Confiar en Ã©l y cargarlo?"
        )

    def cleanup(self):
        for p in (TEMP_JSON, TEMP_SAVE):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
