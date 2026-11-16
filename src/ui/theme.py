import tkinter as tk
from tkinter import ttk

# Colores temáticos Dying Light (Dark Theme)
BG_MAIN = "#1e1e1e"
BG_SECONDARY = "#252526"
BG_CARD = "#2d2d30"
BG_INPUT = "#3c3c3c"
FG_MAIN = "#ffffff"
FG_MUTED = "#aaaaaa"
ACCENT_ORANGE = "#ff7700"
ACCENT_ORANGE_HOVER = "#ff9933"
ACCENT_BLUE = "#007acc"
ACCENT_BLUE_HOVER = "#1f8ad2"
SELECTION_BG = "#094771"
BORDER_COLOR = "#3f3f46"

RARITY_COLORS = {
    "white": "#ffffff",
    "green": "#4caf50",
    "blue": "#2196f3",
    "violet": "#9c27b0",
    "orange": "#ff9800",
    "platinum": "#00e5ff"
}

def apply_dark_theme(root):
    root.configure(bg=BG_MAIN)
    style = ttk.Style(root)
    
    # Usar tema 'clam' como base para personalización total
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Fuentes
    font_main = ("Segoe UI", 9)
    font_bold = ("Segoe UI", 9, "bold")
    font_heading = ("Segoe UI", 10, "bold")

    # Configuración de frames y labels
    style.configure("TFrame", background=BG_MAIN)
    style.configure("Card.TFrame", background=BG_CARD)
    style.configure("TLabel", background=BG_MAIN, foreground=FG_MAIN, font=font_main)
    style.configure("Card.TLabel", background=BG_CARD, foreground=FG_MAIN, font=font_main)
    style.configure("Muted.TLabel", background=BG_MAIN, foreground=FG_MUTED, font=font_main)
    style.configure("Heading.TLabel", background=BG_MAIN, foreground=ACCENT_ORANGE, font=font_heading)

    # Notebook (Pestañas)
    style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
    style.configure("TNotebook.Tab", background=BG_SECONDARY, foreground=FG_MUTED, padding=[12, 6], font=font_bold, borderwidth=0)
    style.map("TNotebook.Tab",
        background=[("selected", BG_CARD), ("active", BG_INPUT)],
        foreground=[("selected", ACCENT_ORANGE), ("active", FG_MAIN)]
    )

    # Treeview
    style.configure("Treeview",
        background=BG_SECONDARY,
        foreground=FG_MAIN,
        fieldbackground=BG_SECONDARY,
        font=font_main,
        rowheight=24,
        borderwidth=0
    )
    style.map("Treeview",
        background=[("selected", SELECTION_BG)],
        foreground=[("selected", FG_MAIN)]
    )
    style.configure("Treeview.Heading",
        background=BG_INPUT,
        foreground=FG_MAIN,
        font=font_bold,
        borderwidth=1,
        relief="flat",
        padding=[6, 4]
    )
    style.map("Treeview.Heading",
        background=[("active", BORDER_COLOR)]
    )

    # Buttons ttk
    style.configure("TButton",
        background=BG_CARD,
        foreground=FG_MAIN,
        font=font_main,
        borderwidth=1,
        relief="flat",
        padding=[8, 4]
    )
    style.map("TButton",
        background=[("pressed", ACCENT_ORANGE), ("active", BG_INPUT)],
        foreground=[("pressed", "#000000"), ("active", FG_MAIN)]
    )

    style.configure("Accent.TButton",
        background=ACCENT_ORANGE,
        foreground="#ffffff",
        font=font_bold,
        padding=[10, 5]
    )
    style.map("Accent.TButton",
        background=[("pressed", "#cc5500"), ("active", ACCENT_ORANGE_HOVER)],
        foreground=[("pressed", "#ffffff"), ("active", "#ffffff")]
    )

    # Entry y Combobox
    style.configure("TEntry",
        fieldbackground=BG_INPUT,
        foreground=FG_MAIN,
        insertcolor=FG_MAIN,
        borderwidth=1
    )
    style.configure("TCombobox",
        fieldbackground=BG_INPUT,
        background=BG_CARD,
        foreground=FG_MAIN,
        selectbackground=SELECTION_BG,
        selectforeground=FG_MAIN,
        arrowcolor=FG_MAIN,
        borderwidth=1
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", BG_INPUT)],
        selectbackground=[("readonly", SELECTION_BG)],
        selectforeground=[("readonly", FG_MAIN)]
    )

    # Scrollbars
    style.configure("Vertical.TScrollbar",
        background=BG_SECONDARY,
        troughcolor=BG_MAIN,
        arrowcolor=FG_MUTED,
        borderwidth=0,
        relief="flat"
    )
    style.map("Vertical.TScrollbar",
        background=[("active", BG_INPUT), ("pressed", ACCENT_ORANGE)]
    )
    style.configure("Horizontal.TScrollbar",
        background=BG_SECONDARY,
        troughcolor=BG_MAIN,
        arrowcolor=FG_MUTED,
        borderwidth=0,
        relief="flat"
    )
    style.map("Horizontal.TScrollbar",
        background=[("active", BG_INPUT), ("pressed", ACCENT_ORANGE)]
    )

    # LabelFrames
    style.configure("TLabelframe",
        background=BG_MAIN,
        foreground=ACCENT_ORANGE,
        font=font_bold,
        borderwidth=1,
        relief="solid"
    )
    style.configure("TLabelframe.Label",
        background=BG_MAIN,
        foreground=ACCENT_ORANGE,
        font=font_bold
    )
