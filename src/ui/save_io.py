"""Carga/guardado de saves, CLI de Steffen y backups."""
from ui.common import *


class SaveIOMixin:
    def _remember_editor(self, path):
        self.save_service.set_editor(path)
        self.editor_exe_path = path
        self.config_data["editor_exe_path"] = path
        save_config(self.config_data)

    def select_editor_cli(self):
        selected = filedialog.askopenfilename(
            title="Select Steffen's CLI (editor.exe)",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        if selected and os.path.exists(selected):
            self._remember_editor(selected)
            messagebox.showinfo("CLI Configured", f"editor.exe set to:\n{selected}")

    def ensure_editor(self):
        """Devuelve la ruta de editor.exe, pidiendola al usuario si hace falta."""
        found = self.save_service.find_editor()
        if found:
            if found != self.editor_exe_path:
                self.editor_exe_path = found
                self.config_data["editor_exe_path"] = found
                save_config(self.config_data)
            return found

        res = messagebox.askyesno(
            "Steffen CLI required",
            "'editor.exe' (Steffen's CLI, needed to decrypt saves) was not found.\n\n"
            "Do you want to locate it manually?\n\n"
            "(If you don't have it, download it from https://steffenl.com/projects/dying-light-save-editor/releases)"
        )
        if res:
            selected = filedialog.askopenfilename(
                title="Select editor.exe (Steffen's CLI)",
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
            )
            if selected and os.path.exists(selected):
                self._remember_editor(selected)
                return selected
        return None

    def _try_begin(self, status_text):
        """Marca la app como ocupada de forma atomica. False si ya habia una operacion."""
        with self._op_lock:
            if self.is_busy:
                return False
            self.set_busy(True, status_text)
            return True

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

        if not self.ensure_editor():
            return

        if not self._try_begin("Decrypting save file with Steffen CLI..."):
            return

        threading.Thread(
            target=self._worker_load_save,
            args=(path,),
            daemon=True
        ).start()

    def _worker_load_save(self, path):
        try:
            data = self.save_service.load(path)
            self.after(0, lambda: self._on_load_success(path, data))
        except Exception as e:
            print(f"[LOAD ERROR] {e}")
            msg = str(e) if isinstance(e, SaveError) else f"Unexpected error reading save:\n{e}"
            self.after(0, lambda m=msg: self._on_load_error(
                f"Could not open the save.\n{m}\n\nMake sure editor.exe is the CLI by Steffen."
            ))

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

        if not self.ensure_editor():
            return

        self.focus()

        # Snapshot profundo: el hilo de guardado no comparte estado con la UI
        data_snapshot = copy.deepcopy(self.current_data)
        save_path = self.save_path

        if not self._try_begin("Creating backup and encrypting save..."):
            return

        if async_mode:
            threading.Thread(
                target=self._worker_save_changes,
                args=(save_path, data_snapshot, on_success, True),
                daemon=True
            ).start()
        else:
            self._worker_save_changes(save_path, data_snapshot, on_success, False)

    def _worker_save_changes(self, save_path, data_snapshot, on_success, is_async=True):
        def dispatch(fn):
            if is_async:
                self.after(0, fn)
            else:
                fn()

        try:
            backup_file = self.save_service.save(save_path, data_snapshot)
        except Exception as e:
            print(f"[SAVE ERROR] {e}")
            err = str(e) if isinstance(e, SaveError) else f"Failed to save changes:\n{e}"
            dispatch(lambda m=err: self._on_save_error(m))
            return
        dispatch(lambda: self._on_save_success(save_path, backup_file, on_success))

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

    # ==================== PLUGINS / CLEANUP ====================
    def _confirm_plugin(self, name, path):
        return messagebox.askyesno(
            "Unverified plugin",
            f"The plugin '{name}' is new or has changed.\n\n{path}\n\n"
            "Plugins run WITHOUT isolation and have full access to your computer.\n"
            "Trust it and load it?"
        )

    def cleanup(self):
        self.save_service.cleanup()
