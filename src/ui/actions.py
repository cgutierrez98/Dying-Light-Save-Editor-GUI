"""Acciones masivas/cheats y plugins."""
from ui.common import *


class ActionsMixin:
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
            messagebox.showerror("Plugin error", f"The plugin '{plugin.get('name')}' failed:\n{e}")

        self.populate()

    def add_legend_skills(self):
        if not self.current_data:
            return

        player = self.current_data.setdefault("player", {})
        buffs = player.setdefault("buffs", [])

        existing = {b.get("name"): b for b in buffs if isinstance(b, dict)}

        for skill in LEGEND_SKILLS:
            skill_name = skill + "_skill"
            if skill_name in existing:
                if existing[skill_name].get("stacks", 0) < 25:
                    existing[skill_name]["stacks"] = 25
            else:
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

    def delete_selected_items(self, tree=None):
        """Elimina de forma segura los elementos seleccionados de cualquier árbol activo."""
        if not self.current_data:
            return

        target_tree = tree or self.current_tree
        if not target_tree:
            return

        selected = target_tree.selection()
        if not selected:
            return

        selected_tab = self.notebook.select() if hasattr(self, "notebook") else ""
        if selected_tab == str(self.tab_skills) or target_tree == getattr(self, "skills_tree", None):
            self.delete_selected_skills()
            return

        count = len(selected)
        confirm_msg = f"Are you sure you want to delete {count} selected item{'s' if count > 1 else ''}?"
        if not messagebox.askyesno("Delete Items", confirm_msg):
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

        deleted_count = 0
        for row_id in selected:
            if (target_tree, row_id) not in self.global_map:
                continue
            _, parent_list, item = self.global_map[(target_tree, row_id)]

            removed = False
            for lst in json_lists:
                if isinstance(lst, list) and item in lst:
                    lst.remove(item)
                    removed = True
                    deleted_count += 1
                    break

            if not removed and isinstance(parent_list, list) and item in parent_list:
                parent_list.remove(item)
                deleted_count += 1

        if getattr(self, "inspector_active_item", None) and (
            getattr(self, "inspector_active_tree", None) == target_tree
        ):
            self.inspector_active_item = None
            self.inspector_active_tree = None
            self.inspector_active_row = None

        self.mark_dirty(True)
        self.populate()
        self.set_status(f"Deleted {deleted_count} item{'s' if deleted_count > 1 else ''}.")

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

    def apply_rarity(self, rarity=None):
        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            return

        r = rarity
        if r is None:
            r = getattr(self, "rarity_var", None)
            r = r.get() if r else "platinum"

        for row_id in selected:
            if (tree, row_id) not in self.global_map:
                continue
            _, _, item = self.global_map[(tree, row_id)]
            set_rarity(item, r)

        self.mark_dirty(True)
        self.populate()

    def set_all_platinum(self):
        if not self.current_data:
            return

        player = self.current_data.get("player", {})
        inventory = player.get("inventory", {})
        storage = player.get("storage", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", []) +
            storage.get("items1", [])
        )

        for item in all_items:
            if isinstance(item, dict):
                set_platinum(item)

        self.mark_dirty(True)
        self.populate()

    def check_ids(self):
        if not self.current_data:
            messagebox.showinfo("Check IDs", "No save file loaded.")
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

        duplicates = get_duplicate_id_map(all_items)

        if not duplicates:
            messagebox.showinfo("Check IDs", "No duplicate IDs found across inventory and stash.")
            return

        msg = ""
        for item_id, items in duplicates.items():
            names = [it.get("name", "Unknown") for it in items[:3]]
            sample = ", ".join(names)
            msg += f"ID {item_id} -> {len(items)} items ({sample})\n"

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

    def apply_craftplan(self, craftplan=None):
        if not self.current_data:
            return

        cp = craftplan
        if cp is None:
            cp_var = getattr(self, "craftplan_var", None)
            cp = cp_var.get() if cp_var else "Craftplan_GodHammer"

        def apply(item):
            if isinstance(item, dict):
                item["craftPlan"] = cp

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

    def apply_weapon_name(self, new_name=None):
        if not self.current_data:
            return

        n = new_name
        if n is None:
            wn_var = getattr(self, "weapon_name_var", None)
            n = wn_var.get() if wn_var else "ZZZZZ_MacheteBKorek2"

        def apply(item):
            if isinstance(item, dict) and "name" in item:
                item["name"] = n

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
