"""Tablas, inspector, stats y portapapeles."""
from ui.common import *


class TablesMixin:
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
                messagebox.showerror("Edit failed", f"Could not apply value '{new_value}':\n{e}")
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
