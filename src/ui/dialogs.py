"""Dialogos auxiliares."""
from ui.common import *


class DialogsMixin:
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
    def show_about(self):
        win = tk.Toplevel(self)
        win.title("About")
        win.geometry("420x240")
        win.configure(bg=BG_MAIN)
        win.transient(self)

        tk.Label(win, text=f"Dying Light Save Editor GUI {CURRENT_VERSION}", bg=BG_MAIN, fg=ACCENT_ORANGE, font=("Segoe UI", 14, "bold")).pack(pady=(20, 5))
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
