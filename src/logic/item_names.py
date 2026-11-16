"""
Diccionario y catálogo exhaustivo de traducción para identificadores técnicos de Dying Light.
Asocia identificadores crudos con nombres legibles y categorías amigables.
"""

ITEM_DICTIONARY = {
    # ==================== ARMAS DE DESARROLLADOR / EASTER EGGS ====================
    "ZZZZZ_MacheteBKorek2": "Machete Korek 2.0 (Legendario Dev)",
    "MacheteAKorek": "Machete Korek 1.0 (Dev)",
    "DevCraftExcalibour": "EXPcalibur (Espada mística clavada)",
    "DevCraftAirStrike": "Ataque Aéreo (Air Strike)",
    "DevRightHandofgloVA": "Mano derecha de gloVA",
    "DevCraftSiCKBomb": "Bomba SiCK",
    "DevCraftPyza": "Traje Pyza (Pyza Suit - Vuelo)",
    "DevCraftTwilightPrism": "Prisma del Crepúsculo (Twilight Prism)",
    "DevCraftStasisGrenade": "Granada de campo de estasis",
    "DevCraftChickenStick": "Pollo en palo (Chicken on a Stick)",
    "DevCraftAntiGadoidGun": "Pistola Anti-Gadoid",
    "DevCraftOrigami101": "Avión de papel Origami 101",
    "DevCraftWorldBestPet": "La mejor mascota del mundo (World's Best Pet)",

    # ==================== ARMAS DORADAS / DE FANTASÍA (GOLD TIER) ====================
    "Melee_ShortSword_Gonunaba": "Gonunaba (Katana de maestro dorada)",
    "Melee_Machete_Loco": "Loco (Machete legendario dorado)",
    "Melee_Knife_Rune": "Daga rúnica (Rune Dagger)",
    "Melee_TwoHandedHammer_Skullmace": "Maza de calavera pesada",
    "Melee_TwoHandedAxe_Baton": "Hacha de batalla pesada",
    "Melee_Pick_Tribal": "Pico tribal dorado",
    "Melee_Sickle_Gold": "Hoz dorada",
    "Melee_Khopesh_Gold": "Jopesh dorado",
    "Melee_Crowbar_Gold": "Palanca dorada",
    "Melee_BaseballBat_Gold": "Bate de béisbol dorado",
    "Melee_Wrench_Gold": "Llave inglesa dorada",
    "Melee_Machete_Dark": "Machete de la oscuridad",
    "Melee_Katana_Gold": "Katana dorada prémium",

    # ==================== ARMAS CUERPO A CUERPO ESTÁNDAR ====================
    "Melee_Machete": "Machete militar",
    "Melee_Katana": "Katana",
    "Melee_ShortSword": "Espada corta",
    "Melee_LongSword": "Espada bastarda",
    "Melee_Khopesh": "Jopesh egipcio (Khopesh)",
    "Melee_TwoHandedAxe": "Hacha pesada a dos manos",
    "Melee_TwoHandedHammer": "Mazo pesado a dos manos",
    "Melee_Axe": "Hacha de mano",
    "Melee_Hammer": "Martillo de demolición",
    "Melee_Pick": "Pico de minero",
    "Melee_Crowbar": "Palanca de acero",
    "Melee_Wrench": "Llave inglesa pesada",
    "Melee_Pipe": "Tubería de gas",
    "Melee_Knife": "Cuchillo táctico de combate",
    "Melee_Sickle": "Hoz afilada",
    "Melee_BaseballBat": "Bate de béisbol reforzado",
    "Melee_Cleaver": "Cuchillo de carnicero (Cleaver)",
    "Melee_Scythe": "Guadaña de la muerte",

    # ==================== ARMAS DE FUEGO ====================
    "Firearm_PistolA": "Pistola americana de 9 mm",
    "Firearm_PistolB": "Pistola alemana de 9 mm",
    "Firearm_Revolver": "Revólver Ranger Six Shooter",
    "Firearm_RifleMilitary": "Fusil de asalto militar",
    "Firearm_RiflePolice": "Fusil policial semiautomático",
    "Firearm_Shotgun": "Escopeta corredera de caza",
    "Firearm_ShotgunDoubleBarrel": "Escopeta recortada de doble cañón",
    "Firearm_Submachine": "Subfusil táctico (SMG)",
    "Firearm_Pistol_Rais": "Pistola personalizada de Rais",
    "Firearm_Rifle_Harran": "Fusil de asalto militar de Harran",
    "Firearm_Shotgun_Rust": "Escopeta de combate oxidada (Rust Shotgun)",

    # ==================== ARCOS Y BALLESTAS ====================
    "Bow_Composite": "Arco compuesto moderno",
    "Bow_Bozak": "Arco de Bozak (Máximo daño)",
    "Bow_Ranger": "Arco del Guardabosques (Harran Ranger)",
    "Crossbow": "Ballesta compuesta de precisión",
    "Crossbow_Upgraded": "Ballesta de cazador mejorada",

    # ==================== ARMAS ARROJADIZAS Y EXPLOSIVAS ====================
    "Throwable_ThrowingStars": "Estrellas ninja (Shurikens)",
    "Throwable_ThrowingStars_Burning": "Estrellas ninja incendiarias",
    "Throwable_ThrowingStars_Freezing": "Estrellas ninja congelantes",
    "Throwable_ThrowingStars_Exploding": "Estrellas ninja explosivas",
    "Throwable_ThrowingKnives": "Cuchillos arrojadizos",
    "Throwable_Molotov": "Cóctel Molotov",
    "Throwable_Grenade": "Granada de fragmentación",
    "Throwable_PoisonGrenade": "Granada de gas venenoso",
    "Throwable_Flashbang": "Granada cegadora / aturdidora",
    "Throwable_Flare": "Bengala UV estándar",
    "Throwable_Flare_Zaid": "Bengala UV potenciada de Zaid",
    "Throwable_Firework": "Petardos de distracción",

    # ==================== HERRAMIENTAS Y EQUIPO ====================
    "Hook": "Gancho de escalada (Grappling Hook)",
    "Lockpick": "Ganzúa estándar",
    "Lockpick_Advanced": "Ganzúa avanzada reforzada",
    "Shield": "Escudo protector antidisturbios",
    "Shield_Claymore": "Escudo con trampa Claymore",

    # ==================== CONSUMIBLES Y POCIONES ====================
    "Medkit_Small": "Botiquín pequeño (+50 HP)",
    "Medkit_Big": "Botiquín grande (+100 HP)",
    "Medkit": "Botiquín médico estándar",
    "Booster_Speed": "Potenciador de velocidad (Speed Booster)",
    "Booster_Stamina": "Potenciador de resistencia infinita",
    "Booster_NightVision": "Potenciador de visión nocturna",
    "Booster_Resistance": "Potenciador de resistencia al daño",
    "Dahlia_MushroomPotion": "Poción de setas de Dahlia",
    "Dahlia_CloakPotion": "Poción de camuflaje de zombi de Dahlia",

    # ==================== MATERIALES DE CRAFTEO ====================
    "Craft_MetalScraps": "Piezas de metal (Metal Scraps)",
    "Craft_Plastic": "Plástico (Plastic)",
    "Craft_Alcohol": "Alcohol",
    "Craft_Gauze": "Gasas médicas (Gauze)",
    "Craft_String": "Cuerda (String)",
    "Craft_DuctTape": "Cinta aislante (Duct Tape)",
    "Craft_Bleach": "Lejía / Cloro (Bleach)",
    "Craft_Chemicals": "Sustancias químicas (Chemicals)",
    "Craft_Batteries": "Pilas / Baterías (Batteries)",
    "Craft_PowerCable": "Cable eléctrico (Power Cable)",
    "Craft_TinCan": "Lata vacía (Tin Can)",
    "Craft_Electronics": "Componentes electrónicos (Electronics)",
    "Craft_Shrooms": "Setas fluorescentes (Fluorescent Mushrooms)",
    "Craft_ToxicPlant": "Hierba venenosa (Toxic Plant)",
    "Craft_Algae": "Algas (Algae)",
    "Craft_UnderwaterAlgae": "Algas submarinas (Underwater Algae)",

    # ==================== TEJIDOS DE INFECTADOS ====================
    "Craft_HunterTissue": "Tejido de cazador nocturno (Hunter Tissue)",
    "Craft_BolterTissue": "Tejido de huidizo (Bolter Tissue)",
    "Craft_PrimeBolterTissue": "Tejido de huidizo alfa (Prime Bolter Tissue)",
    "Craft_BomberTissue": "Tejido de infectado suicida (Bomber Tissue)",
    "Craft_DemolisherTissue": "Tejido de demoledor (Demolisher Tissue)",
    "Craft_VolatileTissue": "Tejido de colérico (Volatile Tissue)",

    # ==================== MUNICIONES ====================
    "Ammo_Pistol": "Munición de pistola (9 mm)",
    "Ammo_Rifle": "Munición de fusil (5.56 mm)",
    "Ammo_Shotgun": "Cartuchos de escopeta",
    "Ammo_SMG": "Munición de subfusil",
    "Ammo_Arrow_Regular": "Flechas comunes de arco",
    "Ammo_Arrow_Fire": "Flechas incendiarias de arco",
    "Ammo_Arrow_Exploding": "Flechas explosivas de arco",
    "Ammo_Arrow_Electric": "Flechas eléctricas de arco",
    "Ammo_Bolt_Regular": "Virotes comunes de ballesta",
    "Ammo_Bolt_Toxic": "Virotes venenosos de ballesta",
    "Ammo_Bolt_Stun": "Virotes aturdidores de ballesta",
    "Ammo_Bolt_Impact": "Virotes de impacto de ballesta",

    # ==================== UPGRADES / MEJORAS DE SOCKETS ====================
    "Craft_Upgrade_DamL2DurL2BalL2": "👑 Rey (King) [+2 Daño, +2 Dur, +2 Manejo]",
    "Craft_Upgrade_DamL2DurL2": "Cruzado (Crusader) [+2 Daño, +2 Dur]",
    "Craft_Upgrade_DamL2BalL2": "Señor de la guerra (Warlord) [+2 Daño, +2 Manejo]",
    "Craft_Upgrade_DurL2BalL2": "Juggernaut [+2 Dur, +2 Manejo]",
    "Craft_Upgrade_DamL2": "Gladiador (Gladiator) [+2 Daño]",
    "Craft_Upgrade_DurL2": "Caballero (Knight) [+2 Dur]",
    "Craft_Upgrade_BalL2": "Paladín (Paladin) [+2 Manejo]",
    "Craft_Upgrade_DamDurBal": "Campeón (Champion) [+1 Daño, +1 Dur, +1 Manejo]",
    "Craft_Upgrade_DamDur": "Templario (Templar) [+1 Daño, +1 Dur]",
    "Craft_Upgrade_DamBal": "Berserker [+1 Daño, +1 Manejo]",
    "Craft_Upgrade_DurBal": "Defensor (Defender) [+1 Dur, +1 Manejo]",
    "Craft_Upgrade_Dam": "Asesino (Assassin) [+1 Daño]",
    "Craft_Upgrade_Dur": "Refuerzo (Reinforcement) [+1 Dur]",
    "Craft_Upgrade_Bal": "Luchador (Brawler) [+1 Manejo]",
    "Craftplan_GTFO20": "GTFO 2.0 (Salto Dev Mod)",
    "Craftplan_LightingRod": "Pararrayos (Lightning Rod)",

    # ==================== CRAFTPLANS / PLANOS ====================
    "Craftplan_GodHammer": "Martillo de Dios (God Hammer) [Fuego 2 + Electricidad 2]",
    "Craftplan_AngelSword": "Espada de Ángel (Angel Sword) [Fuego 2 + Electricidad 2]",
    "Craftplan_AllInOne": "Todo en Uno (All-In-One) [Electricidad 2 + Veneno 2]",
    "Craftplan_ToxicReaper": "Segador Tóxico (Toxic Reaper) [Veneno 2 + Sangrado 2]",
    "Craftplan_Electrician": "Electricista (Electrician) [Electricidad 2]",
    "Craftplan_PoisonBlast": "Explosión Venenosa (Poison Blast) [Veneno 2]",
    "Craftplan_FlapFlap": "Flap Flap [Sangrado 2]",
    "Craftplan_HeavyVenom": "Veneno Pesado (Heavy Venom) [Veneno 2]",
    "Craftplan_BolterPoison": "Veneno de Huidizo (Bolter Poison) [Veneno 2]",
    "Craftplan_ZululsGlow": "Brillo Zulú (Zulu's Glow)",
    "Craftplan_StrobeKnight": "Caballero Estroboscópico [Elec 2 + Sangrado 2]",
    "Craftplan_ElectroChem": "Electro-Químico [Elec 2 + Veneno 2]",
    "Craftplan_BadAss": "Puto Amo (Bad Ass) [Fuego 2 + Impacto 2]",

    # ==================== HABILIDADES LEGENDARIAS ====================
    "LegendSkill_UnarmedDamage": "Daño desarmado / Puños",
    "LegendSkill_OneHandedDamage": "Daño con armas a una mano",
    "LegendSkill_TwoHandedDamage": "Daño con armas a dos manos",
    "LegendSkill_FirearmsDamage": "Daño con armas de fuego",
    "LegendSkill_BowDamage": "Daño con arco y ballesta",
    "LegendSkill_ThrowingDamage": "Daño con armas arrojadizas",
    "LegendSkill_MaxStamina": "Resistencia máxima (Stamina)",
    "LegendSkill_MaxHealth": "Salud máxima (Max Health)",
    "LegendSkill_HealthRegeneration": "Regeneración de salud",
    "LegendSkill_HealingEfficiency": "Eficacia de curación",

    # ==================== COLECCIONABLES ====================
    "ZZZZ_Collectable_CollectableOutfit_01": "Traje coleccionable: Agente secreto",
    "ZZZZ_Collectable_CollectableOutfit_02": "Traje coleccionable: Ropa de corredor",
    "ZZZZ_Collectable_CollectableOutfit_03": "Traje coleccionable: Ropa de explorador",
    "ZZZZ_Collectable_CollectableOutfit_04": "Traje coleccionable: Ninja urbano",
    "ZZZZ_Collectable_CollectableOutfit_05": "Traje coleccionable: Matasanos",
    "ZZZZ_Collectable_CollectableOutfit_06": "Traje coleccionable: Matarife",
    "ZZZZ_Collectable_CollectableOutfit_07": "Traje coleccionable: Deportista Harran",
    "ZZZZ_Collectable_CollectableOutfit_08": "Traje coleccionable: Traje de buzo",
    "ZZZZ_Collectable_CollectableOutfit_09": "Traje coleccionable: Safari nocturno",
    "ZZZZ_Collectable_CollectableOutfit_10": "Traje coleccionable: Burlador de zombis",
    "ZZZZ_Collectable_CollectableOutfit_11": "Traje coleccionable: Cazador de élite",
    "ZZZZ_Collectable_CollectableOutfit_12": "Traje coleccionable: Soldado de Rais"
}


# ==================== CATÁLOGO COMPLETO PARA "AÑADIR ITEM" ====================
ADD_ITEM_PRESETS = [
    # --- Armas de Desarrollador / Legendarias ---
    {"id": "ZZZZZ_MacheteBKorek2", "name": "Machete Korek 2.0 (Dev)", "category": "Armas Legendarias", "is_weapon": True, "qty": 1, "rarity": "orange"},
    {"id": "MacheteAKorek", "name": "Machete Korek 1.0 (Dev)", "category": "Armas Legendarias", "is_weapon": True, "qty": 1, "rarity": "orange"},
    {"id": "DevCraftExcalibour", "name": "EXPcalibur", "category": "Armas Legendarias", "is_weapon": True, "qty": 1, "rarity": "orange"},
    {"id": "DevRightHandofgloVA", "name": "Mano derecha de gloVA", "category": "Armas Legendarias", "is_weapon": True, "qty": 1, "rarity": "orange"},
    {"id": "DevCraftAirStrike", "name": "Ataque Aéreo (Air Strike)", "category": "Armas Legendarias", "is_weapon": True, "qty": 1, "rarity": "orange"},
    {"id": "DevCraftSiCKBomb", "name": "Bomba SiCK", "category": "Armas Legendarias", "is_weapon": True, "qty": 20, "rarity": "orange"},
    {"id": "DevCraftPyza", "name": "Traje Pyza (Planeador)", "category": "Armas Legendarias", "is_weapon": False, "qty": 1, "rarity": "orange"},
    {"id": "DevCraftTwilightPrism", "name": "Prisma del Crepúsculo", "category": "Armas Legendarias", "is_weapon": True, "qty": 1, "rarity": "orange"},
    {"id": "DevCraftStasisGrenade", "name": "Granada de estasis", "category": "Armas Legendarias", "is_weapon": False, "qty": 20, "rarity": "orange"},

    # --- Armas Doradas de Fantasía ---
    {"id": "Melee_ShortSword_Gonunaba", "name": "Gonunaba (Katana dorada)", "category": "Armas de Fantasía", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Machete_Loco", "name": "Loco (Machete dorado)", "category": "Armas de Fantasía", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Knife_Rune", "name": "Daga rúnica", "category": "Armas de Fantasía", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_TwoHandedHammer_Skullmace", "name": "Maza de Calavera", "category": "Armas de Fantasía", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Pick_Tribal", "name": "Pico tribal dorado", "category": "Armas de Fantasía", "is_weapon": True, "qty": 1, "rarity": "platinum"},

    # --- Armas Cuerpo a Cuerpo Comunes ---
    {"id": "Melee_Katana", "name": "Katana prémium", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Machete", "name": "Machete militar", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Khopesh", "name": "Jopesh egipcio", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_TwoHandedAxe", "name": "Hacha pesada a dos manos", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_LongSword", "name": "Espada bastarda", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_TwoHandedHammer", "name": "Mazo pesado a dos manos", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_BaseballBat", "name": "Bate de béisbol reforzado", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Crowbar", "name": "Palanca de acero", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Wrench", "name": "Llave inglesa pesada", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Axe", "name": "Hacha de mano", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Melee_Scythe", "name": "Guadaña de la muerte", "category": "Armas Cuerpo a Cuerpo", "is_weapon": True, "qty": 1, "rarity": "platinum"},

    # --- Armas de Fuego ---
    {"id": "Firearm_Shotgun", "name": "Escopeta corredera", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Firearm_ShotgunDoubleBarrel", "name": "Escopeta de doble cañón", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Firearm_RifleMilitary", "name": "Fusil de asalto militar", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Firearm_RiflePolice", "name": "Fusil policial semiautomático", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Firearm_PistolA", "name": "Pistola americana de 9 mm", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Firearm_PistolB", "name": "Pistola alemana de 9 mm", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Firearm_Revolver", "name": "Revólver Ranger", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Firearm_Submachine", "name": "Subfusil táctico (SMG)", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Firearm_Pistol_Rais", "name": "Pistola de Rais", "category": "Armas de Fuego", "is_weapon": True, "qty": 1, "rarity": "platinum"},

    # --- Arcos y Ballestas ---
    {"id": "Bow_Bozak", "name": "Arco de Bozak", "category": "Arcos y Ballestas", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Bow_Composite", "name": "Arco compuesto moderno", "category": "Arcos y Ballestas", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Bow_Ranger", "name": "Arco Harran Ranger", "category": "Arcos y Ballestas", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Crossbow_Upgraded", "name": "Ballesta de cazador mejorada", "category": "Arcos y Ballestas", "is_weapon": True, "qty": 1, "rarity": "platinum"},
    {"id": "Crossbow", "name": "Ballesta compuesta estándar", "category": "Arcos y Ballestas", "is_weapon": True, "qty": 1, "rarity": "platinum"},

    # --- Materiales de Fabricación Básicos ---
    {"id": "Craft_MetalScraps", "name": "Piezas de metal", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_Plastic", "name": "Plástico", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_Alcohol", "name": "Alcohol", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_Gauze", "name": "Gasas médicas", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_String", "name": "Cuerda", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_DuctTape", "name": "Cinta aislante", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_Bleach", "name": "Lejía / Cloro", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_Chemicals", "name": "Sustancias químicas", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_Batteries", "name": "Pilas / Baterías", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_PowerCable", "name": "Cables de alimentación", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_TinCan", "name": "Latas vacías", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_Electronics", "name": "Componentes electrónicos", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_Shrooms", "name": "Setas fluorescentes", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_ToxicPlant", "name": "Hierba venenosa", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Craft_UnderwaterAlgae", "name": "Algas submarinas", "category": "Materiales", "is_weapon": False, "qty": 99, "rarity": "white"},

    # --- Tejidos de Infectados Raros ---
    {"id": "Craft_HunterTissue", "name": "Tejido de cazador nocturno", "category": "Tejidos Raros", "is_weapon": False, "qty": 50, "rarity": "orange"},
    {"id": "Craft_BolterTissue", "name": "Tejido de huidizo (Bolter)", "category": "Tejidos Raros", "is_weapon": False, "qty": 50, "rarity": "orange"},
    {"id": "Craft_PrimeBolterTissue", "name": "Tejido de huidizo alfa", "category": "Tejidos Raros", "is_weapon": False, "qty": 50, "rarity": "orange"},
    {"id": "Craft_VolatileTissue", "name": "Tejido de colérico", "category": "Tejidos Raros", "is_weapon": False, "qty": 50, "rarity": "orange"},
    {"id": "Craft_DemolisherTissue", "name": "Tejido de demoledor", "category": "Tejidos Raros", "is_weapon": False, "qty": 50, "rarity": "orange"},

    # --- Consumibles, Salud y Herramientas ---
    {"id": "Medkit_Big", "name": "Botiquín grande (+100 HP)", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Medkit_Small", "name": "Botiquín pequeño (+50 HP)", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Medkit", "name": "Botiquín estándar", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Lockpick", "name": "Ganzúas", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Lockpick_Advanced", "name": "Ganzúas avanzadas", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Hook", "name": "Gancho de escalada (Grappling Hook)", "category": "Consumibles", "is_weapon": False, "qty": 1, "rarity": "orange"},
    {"id": "Shield", "name": "Escudo antidisturbios", "category": "Consumibles", "is_weapon": False, "qty": 1, "rarity": "blue"},
    {"id": "Throwable_Flare", "name": "Bengalas UV", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Throwable_Flare_Zaid", "name": "Bengalas UV de Zaid (Potenciadas)", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "orange"},
    {"id": "Throwable_Molotov", "name": "Cócteles Molotov", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Throwable_Grenade", "name": "Granadas de fragmentación", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Throwable_PoisonGrenade", "name": "Granadas de gas venenoso", "category": "Consumibles", "is_weapon": False, "qty": 99, "rarity": "white"},
    {"id": "Booster_Speed", "name": "Potenciador de velocidad", "category": "Consumibles", "is_weapon": False, "qty": 50, "rarity": "blue"},
    {"id": "Booster_Stamina", "name": "Potenciador de resistencia infinita", "category": "Consumibles", "is_weapon": False, "qty": 50, "rarity": "blue"},
    {"id": "Booster_NightVision", "name": "Potenciador de visión nocturna", "category": "Consumibles", "is_weapon": False, "qty": 50, "rarity": "blue"},

    # --- Municiones ---
    {"id": "Ammo_Shotgun", "name": "Munición de escopeta", "category": "Munición", "is_weapon": False, "qty": 100, "rarity": "white"},
    {"id": "Ammo_Rifle", "name": "Munición de fusil militar", "category": "Munición", "is_weapon": False, "qty": 180, "rarity": "white"},
    {"id": "Ammo_Pistol", "name": "Munición de pistola 9 mm", "category": "Munición", "is_weapon": False, "qty": 120, "rarity": "white"},
    {"id": "Ammo_SMG", "name": "Munición de subfusil", "category": "Munición", "is_weapon": False, "qty": 200, "rarity": "white"},
    {"id": "Ammo_Arrow_Regular", "name": "Flechas comunes", "category": "Munición", "is_weapon": False, "qty": 100, "rarity": "white"},
    {"id": "Ammo_Arrow_Exploding", "name": "Flechas explosivas", "category": "Munición", "is_weapon": False, "qty": 100, "rarity": "white"},
    {"id": "Ammo_Arrow_Fire", "name": "Flechas incendiarias", "category": "Munición", "is_weapon": False, "qty": 100, "rarity": "white"},
    {"id": "Ammo_Arrow_Electric", "name": "Flechas eléctricas", "category": "Munición", "is_weapon": False, "qty": 100, "rarity": "white"},
    {"id": "Ammo_Bolt_Regular", "name": "Virotes comunes de ballesta", "category": "Munición", "is_weapon": False, "qty": 100, "rarity": "white"},
    {"id": "Ammo_Bolt_Toxic", "name": "Virotes venenosos de ballesta", "category": "Munición", "is_weapon": False, "qty": 100, "rarity": "white"},
    {"id": "Ammo_Bolt_Impact", "name": "Virotes de impacto de ballesta", "category": "Munición", "is_weapon": False, "qty": 100, "rarity": "white"},

    # --- Coleccionables ---
    {"id": "ZZZZ_Collectable_CollectableOutfit_01", "name": "Traje: Agente secreto", "category": "Coleccionables", "is_weapon": False, "qty": 1, "rarity": "orange"},
    {"id": "ZZZZ_Collectable_CollectableOutfit_04", "name": "Traje: Ninja urbano", "category": "Coleccionables", "is_weapon": False, "qty": 1, "rarity": "orange"},
    {"id": "ZZZZ_Collectable_CollectableOutfit_08", "name": "Traje: Buzo de profundidad", "category": "Coleccionables", "is_weapon": False, "qty": 1, "rarity": "orange"},
    {"id": "ZZZZ_Collectable_CollectableOutfit_11", "name": "Traje: Cazador de élite", "category": "Coleccionables", "is_weapon": False, "qty": 1, "rarity": "orange"}
]


def get_display_name(raw_name):
    """Devuelve el nombre amigable con el ID entre corchetes, o el raw_name si no tiene traducción."""
    if not raw_name:
        return ""
    if raw_name in ITEM_DICTIONARY:
        return f"{ITEM_DICTIONARY[raw_name]} [{raw_name}]"

    if raw_name.startswith("ZZZZ_Collectable_CollectableOutfit_"):
        num = raw_name.replace("ZZZZ_Collectable_CollectableOutfit_", "")
        return f"Traje Coleccionable {num} [{raw_name}]"

    return raw_name


def get_socket_display_name(socket_raw):
    """Devuelve el nombre legible de una mejora de socket."""
    if not socket_raw:
        return "(Vacío / Empty)"
    return ITEM_DICTIONARY.get(socket_raw, socket_raw)


def get_craftplan_display_name(craftplan_raw):
    """Devuelve el nombre legible de un craftplan."""
    if not craftplan_raw:
        return "(Sin plano / None)"
    return ITEM_DICTIONARY.get(craftplan_raw, craftplan_raw)


# ==================== GESTIÓN DE MUNICIÓN (AMMO SLOTS) ====================
AMMO_DEFINITIONS = {
    43: {"name": "Pistola (9 mm)", "icon": "🔫", "max": 999},
    44: {"name": "Fusil militar (5.56 mm)", "icon": "🎖️", "max": 999},
    45: {"name": "Escopeta", "icon": "💥", "max": 999},
    1348: {"name": "Subfusil (SMG)", "icon": "⚡", "max": 999},
    2927: {"name": "Revólver Ranger Six Shooter", "icon": "🤠", "max": 999},
    1335: {"name": "Flechas comunes de arco", "icon": "🏹", "max": 999},
    1336: {"name": "Flechas incendiarias", "icon": "🔥", "max": 999},
    1337: {"name": "Flechas explosivas", "icon": "💣", "max": 999},
    1340: {"name": "Flechas eléctricas", "icon": "⚡", "max": 999},
    2085: {"name": "Virotes comunes de ballesta", "icon": "🎯", "max": 999},
    2086: {"name": "Virotes venenosos de ballesta", "icon": "🧪", "max": 999},
    2087: {"name": "Virotes aturdidores de ballesta", "icon": "💫", "max": 999},
    2088: {"name": "Virotes de impacto de ballesta", "icon": "🚀", "max": 999},
    2089: {"name": "Virotes especiales de ballesta", "icon": "✨", "max": 999},
}


def get_ammo_data(current_data):
    """Extrae la lista de municiones del save asegurando que exista la estructura."""
    if not current_data or not isinstance(current_data, dict):
        return []
    player = current_data.setdefault("player", {})
    inventory = player.setdefault("inventory", {})
    ammo_obj = inventory.setdefault("ammo", {})
    ammo_items = ammo_obj.setdefault("items", [])

    existing_map = {}
    for item in ammo_items:
        if isinstance(item, dict) and "id" in item:
            existing_map[item["id"]] = item

    result = []
    for ammo_id, info in AMMO_DEFINITIONS.items():
        if ammo_id in existing_map:
            val = existing_map[ammo_id].get("value", 0)
        else:
            val = 0
        result.append({
            "id": ammo_id,
            "name": info["name"],
            "icon": info["icon"],
            "value": val
        })
    return result


def set_ammo_value(current_data, ammo_id, value):
    """Actualiza o añade un tipo de munición en el save."""
    if not current_data or not isinstance(current_data, dict):
        return
    player = current_data.setdefault("player", {})
    inventory = player.setdefault("inventory", {})
    ammo_obj = inventory.setdefault("ammo", {})
    ammo_items = ammo_obj.setdefault("items", [])

    for item in ammo_items:
        if isinstance(item, dict) and item.get("id") == ammo_id:
            item["value"] = int(value)
            return

    ammo_items.append({"id": ammo_id, "value": int(value)})


def max_all_ammo(current_data, amount=9999):
    """Establece todas las municiones conocidas al máximo."""
    if not current_data:
        return
    for ammo_id in AMMO_DEFINITIONS.keys():
        set_ammo_value(current_data, ammo_id, amount)

