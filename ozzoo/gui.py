"""
gui.py
======
Tkinter graphical interface for the OzZoo Zoo Simulation — enhanced edition.

Launch via::

    python main.py --gui

or directly::

    python gui.py

Features
--------
* **Dashboard** — live KPI tiles (Balance, Day, Animals, Score) + canvas welfare meters
* **Animals tab** — sortable treeview + right-side detail panel with canvas stat bars
* **Enclosures tab** — treeview + cleanliness / occupancy detail panel
* **Resources tab** — canvas progress bars per food / medicine type; inline buy buttons
* **Finances tab** — three KPI tiles + scrollable ledger treeview
* **Event Log** — color-coded by event type using Text tags
* **Styled dialogs** — every input uses a themed Toplevel (no plain simpledialog)
* **Auto-refresh** — header & dashboard update every 3 s automatically
* No third-party dependencies — stdlib tkinter only.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(__file__))

from zoo import Zoo                          # noqa: E402
from game_loop import GameLoop               # noqa: E402
from patterns.factory import AnimalFactory   # noqa: E402
from finance import Finance                  # noqa: E402
from exceptions import OzZooException        # noqa: E402

SAVE_FILE = "ozzoo_save.json"

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
_BG      = "#1a1a2e"
_PANEL   = "#16213e"
_CARD    = "#0d2137"
_ACCENT  = "#0f3460"
_GOLD    = "#f5a623"
_FG      = "#dde1e7"
_FG2     = "#8891a4"
_BTN_RED = "#e94560"
_BTN_BLU = "#1565c0"
_GREEN   = "#43a047"
_ORANGE  = "#fb8c00"
_RED     = "#e53935"
_CYAN    = "#00acc1"
_PURPLE  = "#8e24aa"
_YELLOW  = "#f9a825"
_TROUGH  = "#2a2a4a"

# Event-log tag colours
_TAG_BIRTH   = "#69f0ae"
_TAG_DEATH   = "#ff1744"
_TAG_WELFARE = "#e53935"
_TAG_FINANCE = "#43a047"
_TAG_RANDOM  = "#f9a825"
_TAG_HABITAT = "#00acc1"

FONT_TITLE  = ("Helvetica", 16, "bold")
FONT_HEAD   = ("Helvetica", 12, "bold")
FONT_BODY   = ("Helvetica", 10)
FONT_SMALL  = ("Helvetica", 9)
FONT_BOLD9  = ("Helvetica", 9, "bold")
FONT_MONO   = ("Courier", 9)
FONT_KPI    = ("Helvetica", 26, "bold")
FONT_KPI_LB = ("Helvetica", 9)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _health_color(value: int) -> str:
    if value >= 70:
        return _GREEN
    if value >= 30:
        return _ORANGE
    return _RED


def _btn(parent, text, cmd, bg=_BTN_BLU, fg=_FG, **kw):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg,
        activebackground=_GOLD, activeforeground="#000",
        relief="flat", padx=10, pady=5,
        font=FONT_BOLD9, cursor="hand2", **kw,
    )


# ---------------------------------------------------------------------------
# Reusable composite widgets
# ---------------------------------------------------------------------------

class _CanvasBar(tk.Canvas):
    """Horizontal filled-bar progress meter drawn on a Canvas."""

    HEIGHT = 16
    RADIUS = 6

    def __init__(self, parent, max_val: int = 100,
                 color: str = _GREEN, bg: str = _PANEL, **kw):
        super().__init__(parent, height=self.HEIGHT,
                         bg=bg, highlightthickness=0, **kw)
        self._max   = max_val
        self._color = color
        self._val   = 0
        self.bind("<Configure>", lambda _e: self._draw())

    def set_value(self, val: int, color: str = "") -> None:
        self._val   = max(0, min(self._max, val))
        if color:
            self._color = color
        self._draw()

    def _draw(self) -> None:
        self.delete("all")
        w = self.winfo_width() or 200
        h = self.HEIGHT
        r = self.RADIUS
        self._rrect(0, 0, w, h, r, fill=_TROUGH)
        fill_w = int(w * self._val / self._max) if self._max else 0
        if fill_w > r * 2:
            self._rrect(0, 0, fill_w, h, r, fill=self._color)
        self.create_text(w // 2, h // 2,
                         text=f"{self._val}/{self._max}",
                         fill=_FG, font=FONT_SMALL, anchor="center")

    def _rrect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
               x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
               x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        self.create_polygon(pts, smooth=True, **kw)


class _KpiTile(tk.Frame):
    """Compact KPI card: big number + unit label."""

    def __init__(self, parent, label: str, unit: str = "",
                 color: str = _GOLD, **kw):
        super().__init__(parent, bg=_CARD, padx=18, pady=12, **kw)
        self._val_var = tk.StringVar(value="—")
        tk.Label(self, text=label, bg=_CARD, fg=_FG2,
                 font=FONT_KPI_LB).pack(anchor="w")
        row = tk.Frame(self, bg=_CARD)
        row.pack(anchor="w")
        tk.Label(row, textvariable=self._val_var, bg=_CARD,
                 fg=color, font=FONT_KPI).pack(side="left")
        if unit:
            tk.Label(row, text=f" {unit}", bg=_CARD,
                     fg=_FG2, font=FONT_BODY).pack(side="left", pady=(8, 0))

    def set(self, value) -> None:
        self._val_var.set(str(value))


class _StatRow(tk.Frame):
    """Label + canvas bar on one horizontal row."""

    def __init__(self, parent, label: str, max_val: int = 100,
                 color: str = _GREEN, **kw):
        super().__init__(parent, bg=_CARD, **kw)
        tk.Label(self, text=label, width=12, anchor="e",
                 bg=_CARD, fg=_FG, font=FONT_SMALL).pack(side="left")
        self._bar = _CanvasBar(self, max_val=max_val, color=color, bg=_CARD)
        self._bar.pack(side="left", fill="x", expand=True, padx=(6, 4))

    def set_value(self, val: int, color: str = "") -> None:
        self._bar.set_value(val, color)


# ---------------------------------------------------------------------------
# Styled dialog classes  (no plain simpledialog)
# ---------------------------------------------------------------------------

class _BaseDialog(tk.Toplevel):
    """Common styling and helpers for all input dialogs."""

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=_BG)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

    def _title_label(self, text: str, cols: int = 2) -> None:
        tk.Label(self, text=text, bg=_BG, fg=_GOLD, font=FONT_HEAD).grid(
            row=0, column=0, columnspan=cols, pady=(16, 10), padx=20)

    def _field(self, label: str, row: int) -> None:
        tk.Label(self, text=label, bg=_BG, fg=_FG, font=FONT_BODY).grid(
            row=row, column=0, sticky="e", padx=10, pady=5)

    def _btn_row(self, ok_text: str, ok_cmd, row: int, cols: int = 2) -> None:
        f = tk.Frame(self, bg=_BG)
        f.grid(row=row, column=0, columnspan=cols, pady=14)
        _btn(f, ok_text, ok_cmd, bg=_BTN_RED).pack(side="left", padx=8)
        _btn(f, "Cancel", self.destroy, bg=_BTN_BLU).pack(side="left", padx=8)


class _BuyAnimalDialog(_BaseDialog):
    def __init__(self, parent):
        super().__init__(parent, "Buy New Animal")
        species_list = AnimalFactory.supported_species()
        self._title_label("🐾  Buy New Animal")

        self._field("Species:", 1)
        self._species_var = tk.StringVar(value=species_list[0])
        ttk.Combobox(self, textvariable=self._species_var,
                     values=species_list, state="readonly", width=22).grid(
            row=1, column=1, padx=10, pady=5)

        self._field("Name:", 2)
        self._name_var = tk.StringVar()
        tk.Entry(self, textvariable=self._name_var, bg=_PANEL, fg=_FG,
                 insertbackground=_FG, width=24).grid(row=2, column=1, padx=10, pady=5)

        self._field("Age (years):", 3)
        self._age_var = tk.IntVar(value=2)
        tk.Spinbox(self, from_=0, to=30, textvariable=self._age_var,
                   bg=_PANEL, fg=_FG, width=8).grid(
            row=3, column=1, sticky="w", padx=10, pady=5)

        self._btn_row("🛒  Buy", self._ok, 4)
        self.wait_window()

    def _ok(self):
        name = self._name_var.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Please enter a name.", parent=self)
            return
        self.result = (self._species_var.get(), name, self._age_var.get())
        self.destroy()


class _MoveAnimalDialog(_BaseDialog):
    def __init__(self, parent, zoo: Zoo):
        super().__init__(parent, "Move Animal")
        self._title_label("🏠  Move Animal to Enclosure")

        names = [a.name for a in zoo.get_alive_animals()]
        self._enc_ids    = [e.enclosure_id for e in zoo.enclosures]
        self._enc_labels = [f"{e.enclosure_id} — {e.name} ({e.habitat_type})"
                            for e in zoo.enclosures]

        self._field("Animal:", 1)
        self._animal_var = tk.StringVar(value=names[0] if names else "")
        ttk.Combobox(self, textvariable=self._animal_var, values=names,
                     state="readonly", width=26).grid(row=1, column=1, padx=10, pady=5)

        self._field("To Enclosure:", 2)
        self._enc_var = tk.StringVar(
            value=self._enc_labels[0] if self._enc_labels else "")
        ttk.Combobox(self, textvariable=self._enc_var, values=self._enc_labels,
                     state="readonly", width=32).grid(row=2, column=1, padx=10, pady=5)

        self._btn_row("Move", self._ok, 3)
        self.wait_window()

    def _ok(self):
        al = self._animal_var.get()
        el = self._enc_var.get()
        if not al or not el:
            return
        idx = self._enc_labels.index(el) if el in self._enc_labels else 0
        self.result = (al, self._enc_ids[idx])
        self.destroy()


class _BuildEnclosureDialog(_BaseDialog):
    HABITATS = ["Savannah", "Arctic", "Wetlands", "Forest", "Desert", "Ocean"]

    def __init__(self, parent):
        super().__init__(parent, "Build New Enclosure")
        self._title_label("🏗️  Build New Enclosure")

        self._field("Name:", 1)
        self._name_var = tk.StringVar()
        tk.Entry(self, textvariable=self._name_var, bg=_PANEL, fg=_FG,
                 insertbackground=_FG, width=24).grid(row=1, column=1, padx=10, pady=5)

        self._field("Habitat Type:", 2)
        self._habitat_var = tk.StringVar(value=self.HABITATS[0])
        ttk.Combobox(self, textvariable=self._habitat_var, values=self.HABITATS,
                     state="readonly", width=22).grid(row=2, column=1, padx=10, pady=5)

        self._field("Max Capacity:", 3)
        self._cap_var = tk.IntVar(value=5)
        tk.Spinbox(self, from_=2, to=20, textvariable=self._cap_var,
                   bg=_PANEL, fg=_FG, width=8).grid(
            row=3, column=1, sticky="w", padx=10, pady=5)

        self._field("Area (m²):", 4)
        self._area_var = tk.DoubleVar(value=200.0)
        tk.Spinbox(self, from_=50, to=2000, increment=50,
                   textvariable=self._area_var, bg=_PANEL, fg=_FG, width=8).grid(
            row=4, column=1, sticky="w", padx=10, pady=5)

        self._btn_row("🏗️  Build", self._ok, 5)
        self.wait_window()

    def _ok(self):
        name = self._name_var.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Please enter a name.", parent=self)
            return
        self.result = (name, self._habitat_var.get(),
                       self._cap_var.get(), self._area_var.get())
        self.destroy()


class _BuyResourceDialog(_BaseDialog):
    """Generic dialog for buying food or medicine."""

    def __init__(self, parent, resource: str, types: list[str],
                 default_type: str, default_qty: int, max_qty: int, unit_label: str):
        super().__init__(parent, f"Buy {resource}")
        self._title_label(f"🛒  Buy {resource}")

        self._field("Type:", 1)
        self._type_var = tk.StringVar(value=default_type)
        ttk.Combobox(self, textvariable=self._type_var, values=types,
                     state="readonly", width=22).grid(row=1, column=1, padx=10, pady=5)

        self._field(f"{unit_label}:", 2)
        self._qty_var = tk.IntVar(value=default_qty)
        tk.Spinbox(self, from_=1, to=max_qty, textvariable=self._qty_var,
                   bg=_PANEL, fg=_FG, width=8).grid(
            row=2, column=1, sticky="w", padx=10, pady=5)

        self._btn_row("Buy", self._ok, 3)
        self.wait_window()

    def _ok(self):
        self.result = (self._type_var.get(), self._qty_var.get())
        self.destroy()


class _SetTicketDialog(_BaseDialog):
    def __init__(self, parent, current: float):
        super().__init__(parent, "Set Ticket Price")
        self._title_label("🎟️  Set Ticket Price")

        self._field("Current price:", 1)
        tk.Label(self, text=f"${current:.2f} AUD", bg=_BG,
                 fg=_GOLD, font=FONT_HEAD).grid(row=1, column=1, padx=10, pady=5)

        self._field("New price ($):", 2)
        self._price_var = tk.DoubleVar(value=current)
        tk.Spinbox(self, from_=0.01, to=500.0, increment=1.0,
                   format="%.2f", textvariable=self._price_var,
                   bg=_PANEL, fg=_FG, width=10).grid(
            row=2, column=1, sticky="w", padx=10, pady=5)

        self._btn_row("Set Price", self._ok, 3)
        self.wait_window()

    def _ok(self):
        self.result = self._price_var.get()
        self.destroy()


class _MedicateDialog(_BaseDialog):
    def __init__(self, parent, animal_name: str):
        super().__init__(parent, "Medicate Animal")
        self._title_label(f"💊  Medicate {animal_name}")

        med_types = ["antibiotic", "vitamin", "vaccine", "painkiller"]
        self._field("Medicine:", 1)
        self._med_var = tk.StringVar(value=med_types[0])
        ttk.Combobox(self, textvariable=self._med_var, values=med_types,
                     state="readonly", width=22).grid(row=1, column=1, padx=10, pady=5)

        self._btn_row("Administer", self._ok, 2)
        self.wait_window()

    def _ok(self):
        self.result = self._med_var.get()
        self.destroy()


# ---------------------------------------------------------------------------
# Main GUI application
# ---------------------------------------------------------------------------

class OzZooGUI:
    """
    The best-possible tkinter GUI for OzZoo.

    Layout
    ------
    Header  — live stats bar (auto-refreshed every 3 s)
    Notebook — 6 tabs:
        📊 Dashboard  |  🐾 Animals  |  🏠 Enclosures
        🛒 Resources  |  💰 Finances  |  📋 Event Log
    Footer  — Advance Day | Save | Load | Quit + Score
    """

    _REFRESH_MS = 3000

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._zoo  = Zoo()
        self._loop = GameLoop(self._zoo)
        self._anim_sort_col: Optional[str] = None
        self._anim_sort_rev: bool = False
        self._event_lines: list[str] = []   # accumulated daily + observer events

        root.title("🦘  OzZoo — Australian Zoo Management")
        root.configure(bg=_BG)
        root.minsize(1040, 680)

        self._setup_styles()
        self._build_header()
        self._build_notebook()
        self._build_footer()
        self._refresh()
        self._schedule_refresh()

    # ------------------------------------------------------------------
    # Style setup
    # ------------------------------------------------------------------

    def _setup_styles(self) -> None:
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TNotebook", background=_BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=_ACCENT, foreground=_FG,
                    padding=[16, 7], font=FONT_BOLD9)
        s.map("TNotebook.Tab",
              background=[("selected", _GOLD)],
              foreground=[("selected", "#000")])
        s.configure("Treeview", background=_PANEL, foreground=_FG,
                    fieldbackground=_PANEL, rowheight=26)
        s.configure("Treeview.Heading", background=_ACCENT, foreground=_GOLD,
                    font=FONT_BOLD9)
        s.map("Treeview",
              background=[("selected", _BTN_RED)],
              foreground=[("selected", "#fff")])
        s.configure("TScrollbar", background=_PANEL, troughcolor=_TROUGH,
                    arrowcolor=_FG)
        s.configure("TCombobox", fieldbackground=_PANEL, background=_PANEL,
                    foreground=_FG, arrowcolor=_FG)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(self) -> None:
        hdr = tk.Frame(self._root, bg=_ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🦘  OzZoo — Australian Zoo Management  🦘",
                 bg=_ACCENT, fg=_GOLD, font=FONT_TITLE).pack()
        self._status_var = tk.StringVar()
        tk.Label(hdr, textvariable=self._status_var, bg=_ACCENT,
                 fg=_FG, font=FONT_BODY).pack(pady=(2, 0))

    # ------------------------------------------------------------------
    # Notebook
    # ------------------------------------------------------------------

    def _build_notebook(self) -> None:
        self._nb = ttk.Notebook(self._root)
        self._nb.pack(fill="both", expand=True, padx=8, pady=(6, 2))
        self._nb.add(self._tab_dashboard(),  text="📊  Dashboard")
        self._nb.add(self._tab_animals(),    text="🐾  Animals")
        self._nb.add(self._tab_enclosures(), text="🏠  Enclosures")
        self._nb.add(self._tab_resources(),  text="🛒  Resources")
        self._nb.add(self._tab_finances(),   text="💰  Finances")
        self._nb.add(self._tab_eventlog(),   text="📋  Event Log")

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------

    def _build_footer(self) -> None:
        foot = tk.Frame(self._root, bg=_ACCENT, pady=9)
        foot.pack(fill="x", side="bottom")
        _btn(foot, "  ⏩  Advance Day  ", self._do_advance_day,
             bg=_BTN_RED).pack(side="left", padx=14)
        _btn(foot, "💾 Save", self._do_save, bg=_BTN_BLU).pack(side="left", padx=4)
        _btn(foot, "📂 Load", self._do_load, bg=_BTN_BLU).pack(side="left", padx=4)
        _btn(foot, "Quit", self._do_quit, bg="#444").pack(side="right", padx=14)
        self._score_var = tk.StringVar(value="Score: 0")
        tk.Label(foot, textvariable=self._score_var, bg=_ACCENT,
                 fg=_GOLD, font=FONT_HEAD).pack(side="right", padx=20)

    # ==================================================================
    # Tab: Dashboard
    # ==================================================================

    def _tab_dashboard(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        # KPI row
        tile_row = tk.Frame(frame, bg=_BG)
        tile_row.pack(fill="x", padx=14, pady=(14, 8))

        self._kpi_balance = _KpiTile(tile_row, "Balance",  "AUD", _GOLD)
        self._kpi_day     = _KpiTile(tile_row, "Day",      "",    _CYAN)
        self._kpi_animals = _KpiTile(tile_row, "Animals",  "",    _GREEN)
        self._kpi_score   = _KpiTile(tile_row, "Score",    "",    _ORANGE)
        for tile in (self._kpi_balance, self._kpi_day,
                     self._kpi_animals, self._kpi_score):
            tile.pack(side="left", fill="x", expand=True, padx=6)

        # Mid row: welfare + stats
        mid = tk.Frame(frame, bg=_BG)
        mid.pack(fill="both", expand=True, padx=14, pady=6)

        welfare_card = tk.Frame(mid, bg=_CARD, padx=14, pady=14)
        welfare_card.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tk.Label(welfare_card, text="🏥  Average Animal Welfare",
                 bg=_CARD, fg=_GOLD, font=FONT_HEAD).pack(anchor="w", pady=(0, 10))
        self._bar_avg_health    = _StatRow(welfare_card, "Health",    color=_GREEN)
        self._bar_avg_hunger    = _StatRow(welfare_card, "Hunger",    color=_ORANGE)
        self._bar_avg_happiness = _StatRow(welfare_card, "Happiness", color=_CYAN)
        for bar in (self._bar_avg_health, self._bar_avg_hunger,
                    self._bar_avg_happiness):
            bar.pack(fill="x", pady=5)

        stats_card = tk.Frame(mid, bg=_CARD, padx=14, pady=14)
        stats_card.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(stats_card, text="📈  Zoo Statistics",
                 bg=_CARD, fg=_GOLD, font=FONT_HEAD).pack(anchor="w", pady=(0, 10))

        self._dash_stat_vars: dict = {}
        dash_rows = [
            ("Total Visitors",  "total_visitors"),
            ("Ticket Price",    "ticket_price"),
            ("Animals Born",    "animals_born"),
            ("Animals Died",    "animals_died"),
            ("Enclosures",      "enclosures"),
        ]
        for label, key in dash_rows:
            row = tk.Frame(stats_card, bg=_CARD)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{label}:", width=16, anchor="w",
                     bg=_CARD, fg=_FG2, font=FONT_SMALL).pack(side="left")
            var = tk.StringVar(value="—")
            tk.Label(row, textvariable=var, bg=_CARD,
                     fg=_FG, font=FONT_BOLD9).pack(side="left")
            self._dash_stat_vars[key] = var

        return frame

    # ==================================================================
    # Tab: Animals
    # ==================================================================

    def _tab_animals(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        cols = ("Name", "Species", "Age", "Health", "Hunger", "Happiness", "Food")
        self._anim_tree = ttk.Treeview(frame, columns=cols,
                                       show="headings", selectmode="browse",
                                       height=16)
        widths = (110, 130, 50, 70, 70, 80, 80)
        for col, w in zip(cols, widths):
            self._anim_tree.heading(col, text=col,
                                    command=lambda c=col: self._sort_animals(c))
            self._anim_tree.column(col, width=w, anchor="center", minwidth=40)

        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self._anim_tree.yview)
        self._anim_tree.configure(yscrollcommand=vsb.set)
        self._anim_tree.pack(side="left", fill="both", expand=True,
                             padx=(8, 0), pady=8)
        vsb.pack(side="left", fill="y", pady=8)
        self._anim_tree.bind("<<TreeviewSelect>>", self._on_animal_select)

        # Detail panel
        detail = tk.Frame(frame, bg=_CARD, padx=12, pady=12, width=230)
        detail.pack(side="right", fill="y", padx=(6, 8), pady=8)
        detail.pack_propagate(False)

        tk.Label(detail, text="Selected Animal", bg=_CARD,
                 fg=_GOLD, font=FONT_HEAD).pack(anchor="w", pady=(0, 6))
        self._detail_name    = tk.Label(detail, text="—", bg=_CARD,
                                        fg=_FG, font=FONT_HEAD)
        self._detail_name.pack(anchor="w")
        self._detail_species = tk.Label(detail, text="", bg=_CARD,
                                        fg=_FG2, font=FONT_SMALL,
                                        justify="left", wraplength=210)
        self._detail_species.pack(anchor="w", pady=(0, 8))

        self._bar_health    = _StatRow(detail, "Health",    color=_GREEN)
        self._bar_hunger    = _StatRow(detail, "Hunger",    color=_ORANGE)
        self._bar_happiness = _StatRow(detail, "Happiness", color=_CYAN)
        for bar in (self._bar_health, self._bar_hunger, self._bar_happiness):
            bar.pack(fill="x", pady=4)

        tk.Frame(detail, bg=_ACCENT, height=1).pack(fill="x", pady=10)

        for text, cmd in [
            ("🍖 Feed",         self._do_feed_animal),
            ("💊 Medicate",     self._do_medicate_animal),
            ("🎭 Make Perform", self._do_perform_animal),
            ("🚚 Move",         self._do_move_animal),
        ]:
            _btn(detail, text, cmd, bg=_BTN_BLU).pack(fill="x", pady=3)

        tk.Frame(detail, bg=_ACCENT, height=1).pack(fill="x", pady=10)
        _btn(detail, "🛒 Buy New Animal", self._do_buy_animal,
             bg=_BTN_RED).pack(fill="x", pady=3)

        return frame

    # ==================================================================
    # Tab: Enclosures
    # ==================================================================

    def _tab_enclosures(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        cols = ("ID", "Name", "Habitat", "Animals", "Cap", "Cleanliness", "Level")
        self._enc_tree = ttk.Treeview(frame, columns=cols,
                                      show="headings", selectmode="browse",
                                      height=16)
        widths = (80, 160, 100, 70, 60, 100, 60)
        for col, w in zip(cols, widths):
            self._enc_tree.heading(col, text=col)
            self._enc_tree.column(col, width=w, anchor="center", minwidth=40)

        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self._enc_tree.yview)
        self._enc_tree.configure(yscrollcommand=vsb.set)
        self._enc_tree.pack(side="left", fill="both", expand=True,
                            padx=(8, 0), pady=8)
        vsb.pack(side="left", fill="y", pady=8)
        self._enc_tree.bind("<<TreeviewSelect>>", self._on_enclosure_select)

        # Detail panel
        detail = tk.Frame(frame, bg=_CARD, padx=12, pady=12, width=210)
        detail.pack(side="right", fill="y", padx=(6, 8), pady=8)
        detail.pack_propagate(False)

        tk.Label(detail, text="Selected Enclosure", bg=_CARD,
                 fg=_GOLD, font=FONT_HEAD).pack(anchor="w", pady=(0, 6))
        self._enc_detail_name = tk.Label(detail, text="—", bg=_CARD,
                                         fg=_FG, font=FONT_HEAD)
        self._enc_detail_name.pack(anchor="w")
        self._enc_detail_info = tk.Label(detail, text="", bg=_CARD,
                                         fg=_FG2, font=FONT_SMALL,
                                         justify="left", wraplength=180)
        self._enc_detail_info.pack(anchor="w", pady=(0, 8))

        self._bar_cleanliness = _StatRow(detail, "Cleanliness", color=_CYAN)
        self._bar_occupancy   = _StatRow(detail, "Occupancy %", color=_PURPLE)
        for bar in (self._bar_cleanliness, self._bar_occupancy):
            bar.pack(fill="x", pady=4)

        tk.Frame(detail, bg=_ACCENT, height=1).pack(fill="x", pady=10)
        for text, cmd in [
            ("🧹 Clean",   self._do_clean_enclosure),
            ("🔧 Upgrade", self._do_upgrade_enclosure),
        ]:
            _btn(detail, text, cmd, bg=_BTN_BLU).pack(fill="x", pady=3)

        tk.Frame(detail, bg=_ACCENT, height=1).pack(fill="x", pady=10)
        _btn(detail, "🏗️ Build New Enclosure", self._do_build_enclosure,
             bg=_BTN_RED).pack(fill="x", pady=3)

        return frame

    # ==================================================================
    # Tab: Resources
    # ==================================================================

    def _tab_resources(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        # Food card
        food_card = tk.Frame(frame, bg=_CARD, padx=14, pady=14)
        food_card.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)

        hdr_f = tk.Frame(food_card, bg=_CARD)
        hdr_f.pack(fill="x", pady=(0, 10))
        tk.Label(hdr_f, text="🌿  Food Inventory", bg=_CARD,
                 fg=_GOLD, font=FONT_HEAD).pack(side="left")
        _btn(hdr_f, "Buy Food", self._do_buy_food, bg=_BTN_RED).pack(side="right")

        self._food_bars: dict[str, _CanvasBar] = {}
        self._food_qty_vars: dict[str, tk.StringVar] = {}
        FOOD_MAX = 100
        for ft in sorted(self._zoo.food_inventory.VALID_TYPES):
            row = tk.Frame(food_card, bg=_CARD)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=ft.capitalize(), width=10, anchor="w",
                     bg=_CARD, fg=_FG, font=FONT_BODY).pack(side="left")
            bar = _CanvasBar(row, max_val=FOOD_MAX, color=_GREEN, bg=_CARD)
            bar.pack(side="left", fill="x", expand=True, padx=6)
            var = tk.StringVar(value="")
            tk.Label(row, textvariable=var, width=10, anchor="e",
                     bg=_CARD, fg=_FG2, font=FONT_SMALL).pack(side="left")
            self._food_bars[ft]     = bar
            self._food_qty_vars[ft] = var

        # Medicine card
        med_card = tk.Frame(frame, bg=_CARD, padx=14, pady=14)
        med_card.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)

        hdr_m = tk.Frame(med_card, bg=_CARD)
        hdr_m.pack(fill="x", pady=(0, 10))
        tk.Label(hdr_m, text="💊  Medicine Inventory", bg=_CARD,
                 fg=_GOLD, font=FONT_HEAD).pack(side="left")
        _btn(hdr_m, "Buy Medicine", self._do_buy_medicine,
             bg=_BTN_RED).pack(side="right")

        self._med_bars: dict[str, _CanvasBar] = {}
        self._med_qty_vars: dict[str, tk.StringVar] = {}
        MED_MAX = 30
        for mt in sorted(self._zoo.medicine_inventory.VALID_TYPES):
            row = tk.Frame(med_card, bg=_CARD)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=mt.capitalize(), width=12, anchor="w",
                     bg=_CARD, fg=_FG, font=FONT_BODY).pack(side="left")
            bar = _CanvasBar(row, max_val=MED_MAX, color=_CYAN, bg=_CARD)
            bar.pack(side="left", fill="x", expand=True, padx=6)
            var = tk.StringVar(value="")
            tk.Label(row, textvariable=var, width=10, anchor="e",
                     bg=_CARD, fg=_FG2, font=FONT_SMALL).pack(side="left")
            self._med_bars[mt]     = bar
            self._med_qty_vars[mt] = var

        return frame

    # ==================================================================
    # Tab: Finances
    # ==================================================================

    def _tab_finances(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        # KPI tiles
        tile_row = tk.Frame(frame, bg=_BG)
        tile_row.pack(fill="x", padx=14, pady=(14, 6))
        self._fin_kpi_balance  = _KpiTile(tile_row, "Current Balance", "AUD", _GOLD)
        self._fin_kpi_income   = _KpiTile(tile_row, "Total Income",    "AUD", _GREEN)
        self._fin_kpi_expenses = _KpiTile(tile_row, "Total Expenses",  "AUD", _RED)
        self._fin_kpi_ticket   = _KpiTile(tile_row, "Ticket Price",    "AUD", _CYAN)
        for tile in (self._fin_kpi_balance, self._fin_kpi_income,
                     self._fin_kpi_expenses, self._fin_kpi_ticket):
            tile.pack(side="left", fill="x", expand=True, padx=6)

        # Action buttons
        btn_row = tk.Frame(frame, bg=_BG)
        btn_row.pack(fill="x", padx=14, pady=(0, 8))
        _btn(btn_row, "🎟️ Set Ticket Price",
             self._do_set_ticket_price, bg=_BTN_RED).pack(side="left", padx=4)
        _btn(btn_row, "📊 Income by Source",
             self._do_income_sources, bg=_BTN_BLU).pack(side="left", padx=4)
        _btn(btn_row, "📉 Expenses by Category",
             self._do_expense_categories, bg=_BTN_BLU).pack(side="left", padx=4)

        # Ledger treeview
        lf = tk.Frame(frame, bg=_BG)
        lf.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        tk.Label(lf, text="Recent Transactions (newest first)",
                 bg=_BG, fg=_FG2, font=FONT_SMALL).pack(anchor="w")

        cols = ("Date", "Type", "Category", "Amount", "Description")
        self._ledger_tree = ttk.Treeview(lf, columns=cols,
                                         show="headings", selectmode="none",
                                         height=10)
        widths = (100, 70, 120, 120, 300)
        anchors = ("center", "center", "center", "center", "w")
        for col, w, anch in zip(cols, widths, anchors):
            self._ledger_tree.heading(col, text=col)
            self._ledger_tree.column(col, width=w, anchor=anch)
        self._ledger_tree.tag_configure("income",  foreground=_GREEN)
        self._ledger_tree.tag_configure("expense", foreground=_RED)

        vsb = ttk.Scrollbar(lf, orient="vertical",
                             command=self._ledger_tree.yview)
        self._ledger_tree.configure(yscrollcommand=vsb.set)
        self._ledger_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        return frame

    # ==================================================================
    # Tab: Event Log
    # ==================================================================

    def _tab_eventlog(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        # Colour legend
        legend = tk.Frame(frame, bg=_BG)
        legend.pack(fill="x", padx=10, pady=(8, 2))
        tk.Label(legend, text="Colour key:", bg=_BG,
                 fg=_FG2, font=FONT_SMALL).pack(side="left", padx=(0, 8))
        for color, label in [
            (_TAG_BIRTH,   "Birth"),
            (_TAG_DEATH,   "Death"),
            (_TAG_WELFARE, "Welfare"),
            (_TAG_FINANCE, "Finance"),
            (_TAG_RANDOM,  "Random event"),
            (_TAG_HABITAT, "Habitat"),
        ]:
            tk.Label(legend, text=f"■ {label}", bg=_BG,
                     fg=color, font=FONT_SMALL).pack(side="left", padx=5)

        # Text area
        self._log_txt = tk.Text(frame, bg=_PANEL, fg=_FG,
                                insertbackground=_FG, relief="flat",
                                font=FONT_MONO, state="disabled", wrap="word")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self._log_txt.yview)
        self._log_txt.configure(yscrollcommand=vsb.set)
        self._log_txt.pack(side="left", fill="both", expand=True,
                           padx=(8, 0), pady=8)
        vsb.pack(side="left", fill="y", pady=8)

        # Tags
        self._log_txt.tag_configure("BIRTH",   foreground=_TAG_BIRTH)
        self._log_txt.tag_configure("DEATH",   foreground=_TAG_DEATH)
        self._log_txt.tag_configure("WELFARE", foreground=_TAG_WELFARE)
        self._log_txt.tag_configure("FINANCE", foreground=_TAG_FINANCE)
        self._log_txt.tag_configure("RANDOM",  foreground=_TAG_RANDOM)
        self._log_txt.tag_configure("HABITAT", foreground=_TAG_HABITAT)
        self._log_txt.tag_configure("DEFAULT", foreground=_FG)

        return frame

    # ==================================================================
    # Refresh logic
    # ==================================================================

    def _schedule_refresh(self) -> None:
        self._update_header()
        self._update_dashboard()
        self._root.after(self._REFRESH_MS, self._schedule_refresh)

    def _refresh(self) -> None:
        self._update_header()
        self._update_dashboard()
        self._update_animals_tree()
        self._update_enclosures_tree()
        self._update_resources_bars()
        self._update_finances()
        self._update_eventlog()

    def _update_header(self) -> None:
        zoo = self._zoo
        self._status_var.set(
            f"Day {zoo.day}  ·  "
            f"Balance: ${zoo.finance.get_balance():,.2f} AUD  ·  "
            f"Visitors today: {len(zoo.daily_visitors)}  ·  "
            f"Animals: {len(zoo.get_alive_animals())}"
        )
        self._score_var.set(f"Score: {zoo.score}")

    def _update_dashboard(self) -> None:
        zoo   = self._zoo
        alive = zoo.get_alive_animals()

        self._kpi_balance.set(f"${zoo.finance.get_balance():,.0f}")
        self._kpi_day.set(zoo.day)
        self._kpi_animals.set(len(alive))
        self._kpi_score.set(zoo.score)

        if alive:
            avg_h  = int(sum(a.health    for a in alive) / len(alive))
            avg_hu = int(sum(a.hunger    for a in alive) / len(alive))
            avg_hp = int(sum(a.happiness for a in alive) / len(alive))
        else:
            avg_h = avg_hu = avg_hp = 0

        self._bar_avg_health.set_value(avg_h,  _health_color(avg_h))
        self._bar_avg_hunger.set_value(avg_hu, _health_color(100 - avg_hu))
        self._bar_avg_happiness.set_value(avg_hp, _health_color(avg_hp))

        stats = {
            "total_visitors": f"{zoo.total_visitors:,}",
            "ticket_price":   f"${zoo.ticket_price:.2f}",
            "animals_born":   str(zoo.animals_born),
            "animals_died":   str(zoo.animals_died),
            "enclosures":     str(len(zoo.enclosures)),
        }
        for k, v in stats.items():
            if k in self._dash_stat_vars:
                self._dash_stat_vars[k].set(v)

    def _update_animals_tree(self) -> None:
        tree = self._anim_tree
        focused  = tree.focus()
        sel_name = tree.item(focused, "values")[0] if focused else None

        for item in tree.get_children():
            tree.delete(item)

        for a in self._zoo.get_alive_animals():
            color = _health_color(a.health)
            tag   = f"h_{a.name}"
            tree.insert("", "end",
                        values=(a.name, a.species, a.age,
                                a.health, a.hunger, a.happiness,
                                a.required_food),
                        tags=(tag,))
            tree.tag_configure(tag, foreground=color)

        if sel_name:
            for item in tree.get_children():
                if tree.item(item, "values")[0] == sel_name:
                    tree.focus(item)
                    tree.selection_set(item)
                    break

        self._refresh_animal_detail()

    def _on_animal_select(self, _event=None) -> None:
        self._refresh_animal_detail()

    def _refresh_animal_detail(self) -> None:
        focused = self._anim_tree.focus()
        if not focused:
            self._detail_name.config(text="—")
            self._detail_species.config(text="")
            for bar in (self._bar_health, self._bar_hunger, self._bar_happiness):
                bar.set_value(0)
            return
        vals = self._anim_tree.item(focused, "values")
        if not vals:
            return
        name, species, age, health, hunger, happiness, food = vals
        self._detail_name.config(text=name)
        self._detail_species.config(
            text=f"{species}  ·  Age {age}  ·  Food: {food}")
        self._bar_health.set_value(int(health),    _health_color(int(health)))
        self._bar_hunger.set_value(int(hunger),    _health_color(100 - int(hunger)))
        self._bar_happiness.set_value(int(happiness), _health_color(int(happiness)))

    def _sort_animals(self, col: str) -> None:
        rev = (self._anim_sort_col == col) and (not self._anim_sort_rev)
        self._anim_sort_col = col
        self._anim_sort_rev = rev
        items = [(self._anim_tree.set(k, col), k)
                 for k in self._anim_tree.get_children()]
        try:
            items.sort(key=lambda x: int(x[0]), reverse=rev)
        except ValueError:
            items.sort(key=lambda x: x[0].lower(), reverse=rev)
        for idx, (_, k) in enumerate(items):
            self._anim_tree.move(k, "", idx)

    def _update_enclosures_tree(self) -> None:
        tree = self._enc_tree
        focused = tree.focus()
        sel_id  = tree.item(focused, "values")[0] if focused else None

        for item in tree.get_children():
            tree.delete(item)

        for enc in self._zoo.enclosures:
            color = _health_color(enc.cleanliness)
            tag   = f"e_{enc.enclosure_id}"
            tree.insert("", "end",
                        values=(enc.enclosure_id, enc.name, enc.habitat_type,
                                enc.animal_count, enc.max_capacity,
                                enc.cleanliness, enc.upgrade_level),
                        tags=(tag,))
            tree.tag_configure(tag, foreground=color)

        if sel_id:
            for item in tree.get_children():
                if tree.item(item, "values")[0] == sel_id:
                    tree.focus(item)
                    tree.selection_set(item)
                    break

        self._refresh_enclosure_detail()

    def _on_enclosure_select(self, _event=None) -> None:
        self._refresh_enclosure_detail()

    def _refresh_enclosure_detail(self) -> None:
        focused = self._enc_tree.focus()
        if not focused:
            self._enc_detail_name.config(text="—")
            self._enc_detail_info.config(text="")
            for bar in (self._bar_cleanliness, self._bar_occupancy):
                bar.set_value(0)
            return
        vals = self._enc_tree.item(focused, "values")
        if not vals:
            return
        enc_id, name, habitat, animals, cap, cleanliness, level = vals
        self._enc_detail_name.config(text=name)
        self._enc_detail_info.config(
            text=f"{enc_id}  ·  {habitat}\n"
                 f"Level {level}  ·  {animals}/{cap} animals")
        self._bar_cleanliness.set_value(int(cleanliness),
                                        _health_color(int(cleanliness)))
        occ_pct = int(100 * int(animals) / int(cap)) if int(cap) > 0 else 0
        self._bar_occupancy.set_value(occ_pct, _health_color(100 - occ_pct))

    def _update_resources_bars(self) -> None:
        FOOD_MAX = 100
        MED_MAX  = 30
        for ft, bar in self._food_bars.items():
            qty = self._zoo.food_inventory.get_quantity(ft)
            bar.set_value(min(qty, FOOD_MAX),
                          _health_color(int(100 * min(qty, FOOD_MAX) / FOOD_MAX)))
            self._food_qty_vars[ft].set(f"{qty} units")
        for mt, bar in self._med_bars.items():
            qty = self._zoo.medicine_inventory.get_quantity(mt)
            bar.set_value(min(qty, MED_MAX),
                          _health_color(int(100 * min(qty, MED_MAX) / MED_MAX)))
            self._med_qty_vars[mt].set(f"{qty} doses")

    def _update_finances(self) -> None:
        fin = self._zoo.finance
        sources = fin.get_income_by_source()
        cats    = fin.get_expenses_by_category()
        total_in  = sum(sources.values())
        total_out = sum(cats.values())

        self._fin_kpi_balance.set(f"${fin.get_balance():,.2f}")
        self._fin_kpi_income.set(f"${total_in:,.2f}")
        self._fin_kpi_expenses.set(f"${total_out:,.2f}")
        self._fin_kpi_ticket.set(f"${self._zoo.ticket_price:.2f}")

        for item in self._ledger_tree.get_children():
            self._ledger_tree.delete(item)

        rows: list[tuple[str, str, str, str, str]] = []
        income_entries, expense_entries = fin.get_recent_ledger(20)
        for ts, amt, cat, desc in income_entries:
            rows.append((ts[:10], "INCOME", cat, f"+${amt:,.2f}", desc))
        for ts, amt, cat, desc in expense_entries:
            rows.append((ts[:10], "EXPENSE", cat, f"-${amt:,.2f}", desc))
        rows.sort(key=lambda r: r[0], reverse=True)
        for row in rows[:20]:
            tag = "income" if row[1] == "INCOME" else "expense"
            self._ledger_tree.insert("", "end", values=row, tags=(tag,))

    def _update_eventlog(self) -> None:
        # Merge accumulated tick lines + any un-cleared observer events
        observer_entries = self._zoo.event_logger.get_recent(80)
        lines = self._event_lines + observer_entries
        if not lines:
            lines = ["(No events yet — advance the day to see activity.)"]

        self._log_txt.configure(state="normal")
        self._log_txt.delete("1.0", "end")
        for line in lines:
            upper = line.upper()
            if "ANIMAL_BORN" in upper or "BABY" in upper or "🍼" in line:
                tag = "BIRTH"
            elif "ANIMAL_DIED" in upper or "DIED" in upper or "💀" in line:
                tag = "DEATH"
            elif "CRITICAL" in upper or "WELFARE" in upper:
                tag = "WELFARE"
            elif "REVENUE" in upper or "BALANCE" in upper or "FINANCE" in upper:
                tag = "FINANCE"
            elif "RANDOM" in upper or "⚡" in line or "🎉" in line:
                tag = "RANDOM"
            elif "HABITAT" in upper or "🏡" in line:
                tag = "HABITAT"
            elif "─" in line or "📅" in line:
                tag = "DEFAULT"
            else:
                tag = "DEFAULT"
            self._log_txt.insert("end", line + "\n", tag)
        self._log_txt.see("end")
        self._log_txt.configure(state="disabled")

    # ==================================================================
    # Selection helpers
    # ==================================================================

    def _selected_animal_name(self) -> Optional[str]:
        focused = self._anim_tree.focus()
        if not focused:
            messagebox.showwarning("No Selection",
                                   "Please select an animal in the list first.")
            return None
        return self._anim_tree.item(focused, "values")[0]

    def _selected_enclosure_id(self) -> Optional[str]:
        focused = self._enc_tree.focus()
        if not focused:
            messagebox.showwarning("No Selection",
                                   "Please select an enclosure in the list first.")
            return None
        return self._enc_tree.item(focused, "values")[0]

    # ==================================================================
    # Action handlers
    # ==================================================================

    def _do_advance_day(self) -> None:
        report = self._loop.tick()
        self._refresh()

        # Accumulate report lines into our event history
        day = self._zoo.day
        self._event_lines.append(f"{'─' * 55}")
        self._event_lines.append(f"📅  Day {day} — Daily Report")
        self._event_lines.append(f"{'─' * 55}")
        for line in report.split("\n"):
            stripped = line.strip()
            if stripped and stripped not in ("─" * 50, "─" * 55):
                self._event_lines.append(line)
        # Also capture any observer events logged today
        for entry in self._zoo.event_logger.get_all_entries():
            ts = entry["timestamp"][:10]
            et = entry["event_type"].upper()
            msg = entry["data"].get("message") or str(entry["data"])
            self._event_lines.append(f"[{ts}] {et}: {msg}")
        self._zoo.event_logger.clear()   # don't double-show on next refresh

        self._update_eventlog()

        dlg = tk.Toplevel(self._root)
        dlg.title(f"📅  Day {self._zoo.day} — Daily Report")
        dlg.configure(bg=_BG)
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg=_ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📅  Day {self._zoo.day} — Daily Report",
                 bg=_ACCENT, fg=_GOLD, font=FONT_HEAD).pack()
        bal = self._zoo.finance.get_balance()
        tk.Label(hdr,
                 text=f"Balance: ${bal:,.2f} AUD  ·  Score: {self._zoo.score}",
                 bg=_ACCENT, fg=_FG, font=FONT_BODY).pack()

        txt = tk.Text(dlg, bg=_PANEL, fg=_FG, insertbackground=_FG,
                      relief="flat", font=FONT_MONO, width=64, height=22,
                      state="normal", wrap="word")
        for tag, color in [("revenue", _GREEN), ("animal", _GOLD),
                            ("dead", _RED), ("random", _YELLOW),
                            ("habitat", _CYAN), ("sep", _FG2)]:
            txt.tag_configure(tag, foreground=color)

        for line in report.split("\n"):
            ul = line.upper()
            if "REVENUE" in ul or "BALANCE" in ul:
                tag = "revenue"
            elif "🐾" in line or "🍼" in line or "ANIMAL" in ul:
                tag = "animal"
            elif "💀" in line or "DIED" in ul:
                tag = "dead"
            elif "⚡" in line or "RANDOM" in ul or "🎉" in line:
                tag = "random"
            elif "🏡" in line or "HABITAT" in ul or "⚠️" in line:
                tag = "habitat"
            elif "─" in line or "=" in line:
                tag = "sep"
            else:
                tag = ""
            txt.insert("end", line + "\n", tag)

        txt.configure(state="disabled")
        vsb = ttk.Scrollbar(dlg, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        txt.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
        vsb.pack(side="left", fill="y", pady=12)
        _btn(dlg, "Close", dlg.destroy, bg=_BTN_BLU).pack(pady=(0, 12))

    def _do_feed_animal(self) -> None:
        name = self._selected_animal_name()
        if name is None:
            return
        try:
            msg = self._zoo.feed_animal(name)
            messagebox.showinfo("Feed Animal", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_medicate_animal(self) -> None:
        name = self._selected_animal_name()
        if name is None:
            return
        dlg = _MedicateDialog(self._root, name)
        if dlg.result is None:
            return
        try:
            msg = self._zoo.medicate_animal(name, dlg.result)
            messagebox.showinfo("Medicate", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_perform_animal(self) -> None:
        name = self._selected_animal_name()
        if name is None:
            return
        try:
            animal = self._zoo.find_animal(name)
            result: Optional[str] = None
            for method in ("jump", "swim", "run", "soar", "snap", "slither", "climb"):
                if hasattr(animal, method):
                    result = getattr(animal, method)()
                    break
            sound = animal.make_sound()
            messagebox.showinfo(f"🎭 {name} Performs",
                                (result or sound) + "\n\n" + sound)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))

    def _do_move_animal(self) -> None:
        dlg = _MoveAnimalDialog(self._root, self._zoo)
        if dlg.result is None:
            return
        animal_name, enc_id = dlg.result
        try:
            msg = self._zoo.move_animal_to_enclosure(animal_name, enc_id)
            messagebox.showinfo("Move Animal", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_buy_animal(self) -> None:
        dlg = _BuyAnimalDialog(self._root)
        if dlg.result is None:
            return
        species, name, age = dlg.result
        try:
            msg = self._zoo.buy_animal(species, name, age)
            messagebox.showinfo("Buy Animal", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_clean_enclosure(self) -> None:
        enc_id = self._selected_enclosure_id()
        if enc_id is None:
            return
        try:
            msg = self._zoo.clean_enclosure(enc_id)
            messagebox.showinfo("Clean", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_upgrade_enclosure(self) -> None:
        enc_id = self._selected_enclosure_id()
        if enc_id is None:
            return
        try:
            msg = self._zoo.upgrade_enclosure(enc_id)
            messagebox.showinfo("Upgrade", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_build_enclosure(self) -> None:
        dlg = _BuildEnclosureDialog(self._root)
        if dlg.result is None:
            return
        name, habitat, cap, area = dlg.result
        try:
            msg = self._zoo.build_enclosure(name, habitat, cap, area)
            messagebox.showinfo("Build Enclosure", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_buy_food(self) -> None:
        dlg = _BuyResourceDialog(
            self._root, "Food",
            sorted(self._zoo.food_inventory.VALID_TYPES),
            "grass", 20, 500, "Units",
        )
        if dlg.result is None:
            return
        food_type, units = dlg.result
        try:
            msg = self._zoo.buy_food(food_type, units)
            messagebox.showinfo("Buy Food", msg)
        except (OzZooException, ValueError) as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_buy_medicine(self) -> None:
        dlg = _BuyResourceDialog(
            self._root, "Medicine",
            sorted(self._zoo.medicine_inventory.VALID_TYPES),
            "antibiotic", 5, 200, "Doses",
        )
        if dlg.result is None:
            return
        med_type, doses = dlg.result
        try:
            msg = self._zoo.buy_medicine(med_type, doses)
            messagebox.showinfo("Buy Medicine", msg)
        except (OzZooException, ValueError) as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_set_ticket_price(self) -> None:
        dlg = _SetTicketDialog(self._root, self._zoo.ticket_price)
        if dlg.result is None:
            return
        try:
            msg = self._zoo.set_ticket_price(dlg.result)
            messagebox.showinfo("Ticket Price", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_income_sources(self) -> None:
        sources = self._zoo.finance.get_income_by_source()
        if not sources:
            messagebox.showinfo("Income by Source", "No income recorded yet.")
            return
        lines = ["Income by Source\n"]
        for src, tot in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {src:<22}  ${tot:>12,.2f} AUD")
        messagebox.showinfo("Income by Source", "\n".join(lines))

    def _do_expense_categories(self) -> None:
        cats = self._zoo.finance.get_expenses_by_category()
        if not cats:
            messagebox.showinfo("Expenses", "No expenses recorded yet.")
            return
        lines = ["Expenses by Category\n"]
        for cat, tot in sorted(cats.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {cat:<22}  ${tot:>12,.2f} AUD")
        messagebox.showinfo("Expenses by Category", "\n".join(lines))

    def _do_save(self) -> None:
        try:
            data = self._zoo.to_dict()
            with open(SAVE_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            messagebox.showinfo("Save Game", f"Game saved to '{SAVE_FILE}'.")
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))

    def _do_load(self) -> None:
        if not os.path.exists(SAVE_FILE):
            messagebox.showerror("Load Error",
                                 f"No save file found ('{SAVE_FILE}').")
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)

            Finance.reset()
            fin = Finance.get_instance()
            fin.from_dict(data.get("finance", {}))

            self._zoo = Zoo(name=data.get("name", "OzZoo"))
            self._zoo.from_dict(data)
            self._loop = GameLoop(self._zoo)
            self._event_lines = []   # clear accumulated events on load
            self._refresh()
            messagebox.showinfo("Load Game", f"Game loaded from '{SAVE_FILE}'.")
        except Exception as exc:
            messagebox.showerror("Load Error", str(exc))

    def _do_quit(self) -> None:
        if messagebox.askyesno("Quit OzZoo",
                               f"Are you sure?\n\nFinal score: {self._zoo.score}"):
            self._root.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_gui() -> None:
    """Create the Tk root and start the OzZoo GUI."""
    root = tk.Tk()
    OzZooGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
