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
from achievements import AchievementTracker, ACHIEVEMENTS, Achievement  # noqa: E402
from challenges import ChallengeTracker, DailyChallenge  # noqa: E402

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
# Utility: star rating
# ---------------------------------------------------------------------------

def _stars(score: int) -> str:
    """Return a ★/☆ string representing the zoo star rating (1–5 stars)."""
    if score >= 250:
        filled = 5
    elif score >= 180:
        filled = 4
    elif score >= 110:
        filled = 3
    elif score >= 50:
        filled = 2
    else:
        filled = 1
    return "★" * filled + "☆" * (5 - filled)


# ---------------------------------------------------------------------------
# Toast notification widget
# ---------------------------------------------------------------------------

class _Toast:
    """
    Transient slide-in banner shown at the top-right of the root window.

    Usage::
        _Toast.show(root, "🏆  Achievement unlocked: Elite Zoo!", colour="#f9a825")
    """
    _DURATION_MS = 3500   # how long the toast is visible
    _SLIDE_STEPS = 12     # animation frames for slide-in
    _SLIDE_DELAY = 16     # ms between animation frames

    @classmethod
    def show(cls, root: tk.Tk, message: str,
             colour: str = "#f9a825", bg: str = "#0f3460") -> None:
        win = tk.Toplevel(root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=bg)

        lbl = tk.Label(win, text=message, bg=bg, fg=colour,
                       font=("Helvetica", 10, "bold"),
                       padx=16, pady=10, wraplength=320, justify="left")
        lbl.pack()

        # Position: top-right of root window
        root.update_idletasks()
        rx = root.winfo_x() + root.winfo_width()
        ry = root.winfo_y() + 60
        w  = 340
        h  = 60

        # Slide in from right
        def _slide(step: int = 0) -> None:
            if not win.winfo_exists():
                return
            progress = min(1.0, step / cls._SLIDE_STEPS)
            x = int(rx - w * progress)
            win.geometry(f"{w}x{h}+{x}+{ry}")
            if step < cls._SLIDE_STEPS:
                root.after(cls._SLIDE_DELAY, _slide, step + 1)
            else:
                root.after(cls._DURATION_MS, lambda: cls._dismiss(win, root, rx, ry, w, h))

        win.geometry(f"{w}x{h}+{rx}+{ry}")
        _slide()

    @classmethod
    def _dismiss(cls, win: tk.Toplevel, root: tk.Tk,
                 rx: int, ry: int, w: int, h: int) -> None:
        """Slide the toast back out to the right."""
        def _slide_out(step: int = 0) -> None:
            if not win.winfo_exists():
                return
            progress = min(1.0, step / cls._SLIDE_STEPS)
            x = int(rx - w + w * progress)
            win.geometry(f"{w}x{h}+{x}+{ry}")
            if step < cls._SLIDE_STEPS:
                root.after(cls._SLIDE_DELAY, _slide_out, step + 1)
            else:
                win.destroy()
        _slide_out()


# ---------------------------------------------------------------------------
# Achievement Gallery dialog
# ---------------------------------------------------------------------------

class _AchievementsDialog(tk.Toplevel):
    """Modal gallery showing all achievements and their unlock status."""

    def __init__(self, parent: tk.Widget,
                 tracker: "AchievementTracker") -> None:
        super().__init__(parent)
        self.title("🏅  Achievements")
        self.configure(bg=_BG)
        self.resizable(True, True)
        self.geometry("720x520")
        self.grab_set()
        self._tracker = tracker
        self._build()

    def _build(self) -> None:
        # Header
        hdr = tk.Frame(self, bg=_ACCENT, pady=10)
        hdr.pack(fill="x")
        count   = self._tracker.unlocked_count
        total   = self._tracker.total_count
        pct     = round(count / total * 100) if total else 0
        tk.Label(hdr, text=f"🏅  Achievements  —  {count}/{total} unlocked  ({pct}%)",
                 bg=_ACCENT, fg=_GOLD, font=FONT_HEAD).pack()

        # Scrollable grid
        container = tk.Frame(self, bg=_BG)
        container.pack(fill="both", expand=True, padx=10, pady=8)

        canvas = tk.Canvas(container, bg=_BG, highlightthickness=0)
        vsb    = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=_BG)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        unlocked = self._tracker.unlocked_keys
        # 3 columns here (dialog is 720 px wide) vs 4 in the tab (full window width)
        cols = 3
        for idx, ach in enumerate(ACHIEVEMENTS):
            row, col = divmod(idx, cols)
            locked = ach.key not in unlocked
            card_bg = _PANEL if not locked else _CARD
            fg_main = _FG if not locked else _FG2
            fg_sub  = _FG2 if not locked else "#555"

            card = tk.Frame(inner, bg=card_bg, padx=10, pady=8,
                            relief="flat", bd=0,
                            highlightbackground=(_GOLD if not locked else "#2a2a4a"),
                            highlightthickness=1)
            card.grid(row=row, column=col, padx=6, pady=5, sticky="nsew")
            inner.columnconfigure(col, weight=1)

            top = tk.Frame(card, bg=card_bg)
            top.pack(fill="x")
            icon_lbl = tk.Label(top, text=ach.icon if not locked else "🔒",
                                bg=card_bg, fg=_GOLD if not locked else _FG2,
                                font=("Helvetica", 18))
            icon_lbl.pack(side="left", padx=(0, 8))
            tk.Label(top, text=ach.title, bg=card_bg,
                     fg=fg_main, font=FONT_BOLD9).pack(side="left", anchor="w")

            tk.Label(card, text=ach.description, bg=card_bg,
                     fg=fg_sub, font=FONT_SMALL,
                     wraplength=180, justify="left").pack(anchor="w")
            if ach.reward > 0:
                reward_fg = _GREEN if not locked else _FG2
                tk.Label(card, text=f"Reward: +${ach.reward:,.0f} AUD",
                         bg=card_bg, fg=reward_fg, font=FONT_SMALL).pack(anchor="w")

        # Footer
        foot = tk.Frame(self, bg=_ACCENT, pady=8)
        foot.pack(fill="x", side="bottom")
        _btn(foot, "Close", self.destroy, bg=_BTN_BLU).pack()


# ---------------------------------------------------------------------------
# How-to-Play dialog
# ---------------------------------------------------------------------------

# ── Content is defined as (heading, body_lines) tuples per section ────────
# Line prefix markers used by _HelpDialog._show_section() for colour coding:
#   "## " → subheading (cyan)   "++ " → good (green)   "!! " → danger (red)
#   "~~ " → warning (orange)    ">> " → highlight (yellow)   (no prefix) → plain
_HELP_SECTIONS = [
    (
        "🎮  Overview",
        [
            "Welcome to OzZoo — Australian Zoo Management!",
            "",
            "You are the manager of an Australian wildlife zoo.  Your goal is to",
            "build and maintain a thriving zoo by:",
            "  • Keeping your animals healthy, fed, and happy",
            "  • Attracting visitors and maximising ticket revenue",
            "  • Expanding your enclosures and growing your animal collection",
            "  • Surviving random events and managing your finances",
            "",
            "The game has no fixed end date — play as long as you like and aim",
            "for the highest Score possible.",
        ],
    ),
    (
        "📊  Dashboard",
        [
            "The Dashboard gives you a live overview of your zoo:",
            "",
            "## KPI Tiles (top row)",
            "  ─────────────────",
            "  • Balance    — Your current cash in AUD.  Never let it hit $0!",
            "  • Day        — How many days your zoo has been open.",
            "  • Animals    — Number of living animals in your zoo.",
            "  • Score      — Your overall performance rating (see Scoring).",
            "",
            "## Average Animal Welfare (left panel)",
            "  ────────────────────────────────────",
            "  • Health     — Average health across all animals (0-100).",
            "  • Hunger     — Average hunger level.  High hunger is bad!",
            "  • Happiness  — Average happiness across all animals (0-100).",
            "",
            "  Bar colours:",
            "++ Green (≥70) = great   — no action needed",
            "~~ Orange (30–69) = caution  — monitor closely",
            "!! Red (<30) = critical  — take immediate action!",
            "",
            "## Zoo Statistics (right panel)",
            "  ────────────────────────────",
            "  Cumulative visitor count, ticket price, births, deaths, and",
            "  number of enclosures.",
        ],
    ),
    (
        "🐾  Animals",
        [
            "The Animals tab lists every living animal in your zoo.",
            "",
            "## Columns",
            "  Name · Species · Age · Health (0-100) · Hunger (0-100)",
            "  Happiness (0-100) · Required Food",
            "",
            "  Click any column heading to sort ascending / descending.",
            "  Select a row → the right-hand Detail Panel updates with",
            "  canvas stat bars for that individual animal.",
            "",
            "## Actions (Detail Panel buttons)",
            "  ──────────────────────────────",
            "  🍖 Feed         — Feed the selected animal.  Reduces hunger",
            "                    and boosts happiness.  Requires food stock",
            "                    of the animal's type (grass / meat / fish /",
            "                    fruit / insects).  Cost: ~$2–8/unit.",
            "",
            "  💊 Medicate     — Administer medicine.  Choose:",
            "    antibiotic  $20/dose  +30 HP",
            "    vitamin      $8/dose  +10 HP",
            "    painkiller  $12/dose  +15 HP",
            "++ vaccine     $25/dose  +40 HP  ← best value after outbreaks",
            "",
            "  🎭 Make Perform — Triggers the animal's special ability",
            "                    and plays its sound.  Free action.",
            "",
            "  🚚 Move         — Transfer to a different enclosure.",
            "                    Pair same species to enable breeding.",
            "",
            "  🛒 Buy New      — Purchase a new animal.  Prices:",
            "    Snake $250  ·  Emu $300  ·  Penguin $350",
            "    Koala $400  ·  Kangaroo $500  ·  Eagle $600",
            "    Crocodile $800",
            "",
            "## Daily mechanics per animal",
            "!! Every day: hunger +10, happiness -3.",
            "!! Hunger > 80 for 2 consecutive days → health -10/day.",
            "!! Happiness < 20 → health -5/day.",
            "!! Health reaches 0 → animal dies permanently.",
        ],
    ),
    (
        "🏠  Enclosures",
        [
            "Enclosures house your animals and degrade over time.",
            "",
            "## Columns",
            "  ID · Name · Habitat Type · Animals (current) · Capacity",
            "  Cleanliness (0-100) · Upgrade Level",
            "",
            "  Select a row → Detail Panel shows canvas bars for",
            "  Cleanliness and Occupancy %.",
            "",
            "## Actions",
            "  🧹 Clean       — Restores cleanliness to 100.  Cost: $50.",
            "~~ Enclosures lose 10 cleanliness per day.",
            "!! Below 30 cleanliness → animals lose happiness.",
            "  Recommended: clean every 2–3 days.",
            "",
            "  🔧 Upgrade     — Increases upgrade level by 1.  Cost: $500.",
            "                   Higher levels improve animal happiness and",
            "                   visitor satisfaction ratings.",
            "",
            "  🏗️ Build New   — Construct a new enclosure.",
            "                   Cost: $1,000 + $2 per m² of area.",
            "                   Match the habitat type to your animals'",
            "                   natural environment.",
            "",
            "## Breeding",
            "  When two animals of the same species share an enclosure,",
            "  there is a daily chance of a new baby being born for free!",
            "++ This is one of the best ways to grow your collection",
            "++ without spending any money.",
        ],
    ),
    (
        "🛒  Resources",
        [
            "Keep your food and medicine stocked — running out is dangerous.",
            "",
            "## Food Types & Prices",
            "  Grass    $2.00 / unit   — Kangaroos, Koalas, Emus",
            "  Fruit    $3.00 / unit   — Koalas",
            "  Insects  $1.50 / unit   — Cheapest option (Snakes)",
            "  Fish     $6.00 / unit   — Penguins",
            "  Meat     $8.00 / unit   — Crocodiles, Eagles",
            "",
            "  Each animal eats 1 unit of its required food per feeding.",
            "!! Feed animals daily to keep hunger below 70.",
            "",
            "## Medicine Types & Prices",
            "  Antibiotic  $20 / dose  +30 HP",
            "  Vitamin      $8 / dose  +10 HP",
            "  Painkiller  $12 / dose  +15 HP",
            "++ Vaccine     $25 / dose  +40 HP  ← best value per HP",
            "",
            "  Progress bars turn red when stock is critically low.",
            "  Buy in bulk to save trips — but watch your balance!",
            "",
            ">> Tip: Buy grass and fruit in batches of 50+ (cheapest)",
            ">> and keep at least 5 vaccine doses on hand at all times.",
        ],
    ),
    (
        "💰  Finances",
        [
            "Revenue comes in every time you advance a day.",
            "",
            "## Income Sources",
            "  Ticket Sales   — Daily visitors × ticket price.",
            "                   Visitor count ≈ 20 + (avg_health / 5)",
            "                   ± random variance each day.",
            "                   Default ticket price: $25.00 AUD.",
            "",
            "  Donations      — Received from Zoo Celebration and",
            "                   Donation Drive random events ($200–$2,000).",
            "",
            "## Setting Ticket Price",
            "  Higher price → more revenue per visitor.",
            "  Fewer happy animals → fewer visitors.",
            ">> Optimal ticket price: $20–$35 to keep visitors coming.",
            "",
            "## Expenses",
            "  Animal purchases · Food · Medicine · Cleaning ($50) ·",
            "  Enclosure upgrades ($500) · Construction ($1,000+) ·",
            "  Escape fines ($100–$500 random event)",
            "",
            "!! Balance below $1,000 AUD → LOW FUNDS alert fires.",
            "!! Balance reaches $0 → cannot buy anything; zoo collapses.",
            "",
            "## Ledger",
            "  The Recent Transactions treeview shows the last 20",
            "  transactions in green (income) and red (expense).",
        ],
    ),
    (
        "⚡  Random Events",
        [
            "Each day has a 25% chance of a random event.  Be prepared!",
            "",
            "## 🌡️  Heatwave",
            "   All animals -5 health, -10 happiness.",
            ">> Remedy: medicate and feed immediately after.",
            "",
            "## 🎉  Zoo Celebration",
            "++ Bonus donation $200–$800 AUD.  Great day!",
            "",
            "## 🚨  Animal Escape",
            "~~ Fine of $100–$500 AUD to recapture the animal.",
            ">> Keep $1,500+ in the bank to absorb this cost.",
            "",
            "## 🦠  Disease Outbreak",
            "!! Animals in one random enclosure lose 10–25 HP each.",
            ">> Remedy: immediately vaccinate/medicate affected animals.",
            "",
            "## 💝  Donation Drive",
            "++ Large donation of $300–$2,000 AUD.  Best event!",
            "",
            "## 🍼  Baby Boom",
            "++ 1–3 random baby animals added for free.",
        ],
    ),
    (
        "🏆  Scoring & Winning",
        [
            "Your Score updates every time you advance a day.",
            "",
            "## Score Formula",
            "  Score =  avg_health    × 0.35  (0–100)",
            "         + avg_happiness × 0.25  (0–100)",
            "         + avg_visitor_sat × 0.20  (visitor satisfaction)",
            "         + unique_species × 5     (species diversity bonus)",
            "         + financial_score × 0.20 (capped at 100)",
            "",
            "  financial_score = min(100, balance / $1,000 × 10)",
            "++ $10,000 balance = perfect financial score of 100",
            "",
            "## Score Tiers",
            "   0–49    Struggling zoo — animals are suffering",
            "   50–99   Average zoo — room for improvement",
            "   100–149 Good zoo — visitors are happy",
            "   150–199 Great zoo — thriving animals and finances",
            "++ 200+    Elite zoo — Australian wildlife paradise! 🏆",
            "",
            "## How to maximise your score",
            ">> 1. Keep ALL animals at Health ≥ 70 and Hunger < 30",
            ">> 2. Clean enclosures regularly (every 2–3 days: $50 each)",
            ">> 3. Collect all 7 species for max diversity bonus (×5 each)",
            ">> 4. Keep balance above $10,000 for max financial score",
            ">> 5. Set ticket price at $25–$30 for optimal visitor flow",
            ">> 6. Breed animals cheaply via shared enclosures",
            ">> 7. Upgrade enclosures to boost visitor satisfaction",
            ">> 8. After a Disease Outbreak, vaccinate immediately",
        ],
    ),
    (
        "💡  Quick-Start Tips",
        [
            "## Day 0 (before advancing)",
            "  Your zoo starts with 8 animals, 4 enclosures, $10,000.",
            "  All animals are at full health (100 HP), hunger 0, happiness 80.",
            "",
            "## Day 1",
            "  Press Advance Day — read the Daily Report popup.",
            "  Animals: hunger now 10, happiness 77.  No action needed yet.",
            "",
            "## Days 2–5",
            ">> Feed every animal as hunger approaches 70.",
            ">> Clean enclosures when cleanliness drops below 50 ($50 each).",
            "~~ If a random event hit, medicate affected animals immediately.",
            ">> Consider buying a second species for the +5 score bonus.",
            "",
            "## Days 6–15",
            ">> Experiment with ticket price — try $28–$32 on the Finances tab.",
            ">> Put two Kangaroos or Koalas in one enclosure for free breeding.",
            ">> Build a new enclosure if animals exceed capacity ($1,200+).",
            "++ Target Score 100+ by day 10.",
            "",
            "## Long term",
            ">> Collect all 7 species for maximum diversity bonus.",
            ">> Keep $2,000+ cash buffer against escapes and outbreaks.",
            "++ Target Score 200+ by day 30.",
            ">> Save your game regularly with the Save button.",
        ],
    ),
]


class _HelpDialog(tk.Toplevel):
    """
    Scrollable, tabbed How-to-Play reference dialog.

    Opens as a modal window with a sidebar list of sections and a
    right-hand content area that updates when a section is selected.
    """

    _WIDTH  = 820
    _HEIGHT = 560

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.title("❓  How to Play OzZoo")
        self.configure(bg=_BG)
        self.resizable(True, True)
        self.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        self.grab_set()
        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        # ── Header ────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=_ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="❓  How to Play OzZoo — Complete Guide",
                 bg=_ACCENT, fg=_GOLD, font=FONT_HEAD).pack()

        # ── Body: sidebar + content ────────────────────────────────────
        body = tk.Frame(self, bg=_BG)
        body.pack(fill="both", expand=True, padx=8, pady=6)

        # Sidebar list-box
        sidebar = tk.Frame(body, bg=_PANEL, width=190)
        sidebar.pack(side="left", fill="y", padx=(0, 6))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Sections", bg=_PANEL, fg=_GOLD,
                 font=FONT_BOLD9).pack(anchor="w", padx=8, pady=(8, 4))

        self._listbox = tk.Listbox(
            sidebar,
            bg=_PANEL, fg=_FG, selectbackground=_BTN_RED,
            selectforeground="#fff", activestyle="none",
            relief="flat", font=FONT_SMALL, borderwidth=0,
            highlightthickness=0,
        )
        for heading, _ in _HELP_SECTIONS:
            self._listbox.insert("end", f"  {heading}")
        self._listbox.pack(fill="both", expand=True, padx=4, pady=(0, 8))
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        # Content area
        content_frame = tk.Frame(body, bg=_BG)
        content_frame.pack(side="left", fill="both", expand=True)

        self._section_title = tk.Label(
            content_frame, text="", bg=_BG, fg=_GOLD, font=FONT_HEAD,
            anchor="w",
        )
        self._section_title.pack(anchor="w", padx=6, pady=(4, 6))

        self._text = tk.Text(
            content_frame, bg=_CARD, fg=_FG, insertbackground=_FG,
            relief="flat", font=FONT_MONO, state="disabled",
            wrap="word", padx=12, pady=10,
        )
        vsb = ttk.Scrollbar(content_frame, orient="vertical",
                             command=self._text.yview)
        self._text.configure(yscrollcommand=vsb.set)
        self._text.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        # Configure text tags for colour highlights
        self._text.tag_configure("heading",    foreground=_GOLD,   font=FONT_BOLD9)
        self._text.tag_configure("subheading", foreground=_CYAN,   font=FONT_BOLD9)
        self._text.tag_configure("good",       foreground=_GREEN)
        self._text.tag_configure("warn",       foreground=_ORANGE)
        self._text.tag_configure("danger",     foreground=_RED)
        self._text.tag_configure("highlight",  foreground=_YELLOW)

        # Footer close button
        foot = tk.Frame(self, bg=_ACCENT, pady=8)
        foot.pack(fill="x", side="bottom")
        _btn(foot, "Close", self.destroy, bg=_BTN_BLU).pack()

        # Select first section by default
        self._listbox.selection_set(0)
        self._show_section(0)

    # ------------------------------------------------------------------
    def _on_select(self, _event=None) -> None:
        sel = self._listbox.curselection()
        if sel:
            self._show_section(sel[0])

    def _show_section(self, idx: int) -> None:
        heading, lines = _HELP_SECTIONS[idx]
        self._section_title.config(text=heading)

        self._text.configure(state="normal")
        self._text.delete("1.0", "end")

        # Prefix markers embedded in _HELP_SECTIONS data drive colour tags:
        #   "## " → subheading (cyan)    "++ " → good (green)
        #   "!! " → danger (red)         "~~ " → warning (orange)
        #   ">> " → highlight (yellow)   (no prefix) → plain text
        _PREFIX_TAG = {
            "## ": "subheading",
            "++ ": "good",
            "!! ": "danger",
            "~~ ": "warn",
            ">> ": "highlight",
        }
        for line in lines:
            tag = ""
            display = line
            for prefix, t in _PREFIX_TAG.items():
                if line.startswith(prefix):
                    tag = t
                    display = line[len(prefix):]
                    break
            self._text.insert("end", display + "\n", tag)

        self._text.configure(state="disabled")
        self._text.see("1.0")


# ---------------------------------------------------------------------------
# Main GUI application
# ---------------------------------------------------------------------------

class OzZooGUI:
    """
    The best-possible tkinter GUI for OzZoo.

    Layout
    ------
    Header  — live stats bar with news ticker + star rating (auto-refreshed every 3 s)
    Notebook — 7 tabs:
        📊 Dashboard  |  🐾 Animals  |  🏠 Enclosures
        🛒 Resources  |  💰 Finances  |  📋 Event Log  |  🏅 Achievements
    Footer  — Advance Day | Save | Load | How to Play | Quit + Score
    """

    _REFRESH_MS   = 3000
    _TICKER_DELAY = 60    # ms per character scroll step
    _TICKER_WIDTH = 90    # visible characters in the news ticker

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._zoo  = Zoo()
        self._loop = GameLoop(self._zoo)
        self._anim_sort_col: Optional[str] = None
        self._anim_sort_rev: bool = False
        self._event_lines: list[str] = []   # accumulated daily + observer events

        # Addictive-gameplay systems
        self._achievements  = AchievementTracker()
        self._challenges    = ChallengeTracker()
        self._no_death_streak: int   = 0
        self._prev_score:      int   = 0
        self._best_score:      int   = 0
        self._ticker_msgs:     list[str] = ["Welcome to OzZoo! 🦘  Advance the day to begin!"]
        self._ticker_pos:      int   = 0

        # Daily-challenge state
        self._current_challenge: Optional[DailyChallenge] = None
        self._challenge_result:  Optional[tuple[bool, float]] = None

        root.title("🦘  OzZoo — Australian Zoo Management")
        root.configure(bg=_BG)
        root.minsize(1100, 720)  # wider than original to fit 7-tab notebook + challenge panel

        self._setup_styles()
        self._build_header()
        self._build_notebook()
        self._build_footer()
        self._refresh()
        self._schedule_refresh()
        self._schedule_ticker()


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
        hdr = tk.Frame(self._root, bg=_ACCENT, pady=6)
        hdr.pack(fill="x")

        # Title row with star rating
        title_row = tk.Frame(hdr, bg=_ACCENT)
        title_row.pack()
        tk.Label(title_row, text="🦘  OzZoo — Australian Zoo Management  🦘",
                 bg=_ACCENT, fg=_GOLD, font=FONT_TITLE).pack(side="left")
        self._stars_var = tk.StringVar(value="  ☆☆☆☆☆")
        tk.Label(title_row, textvariable=self._stars_var,
                 bg=_ACCENT, fg=_GOLD, font=("Helvetica", 14)).pack(side="left", padx=(12, 0))

        # Status line
        self._status_var = tk.StringVar()
        tk.Label(hdr, textvariable=self._status_var, bg=_ACCENT,
                 fg=_FG, font=FONT_BODY).pack(pady=(2, 0))

        # News ticker
        ticker_frame = tk.Frame(hdr, bg="#0d1a30", pady=3)
        ticker_frame.pack(fill="x", padx=0, pady=(4, 0))
        self._ticker_var = tk.StringVar(value="")
        tk.Label(ticker_frame, textvariable=self._ticker_var,
                 bg="#0d1a30", fg=_CYAN, font=FONT_MONO,
                 anchor="w").pack(fill="x", padx=10)

    # ------------------------------------------------------------------
    # Notebook
    # ------------------------------------------------------------------

    def _build_notebook(self) -> None:
        self._nb = ttk.Notebook(self._root)
        self._nb.pack(fill="both", expand=True, padx=8, pady=(6, 2))
        self._nb.add(self._tab_dashboard(),    text="📊  Dashboard")
        self._nb.add(self._tab_animals(),      text="🐾  Animals")
        self._nb.add(self._tab_enclosures(),   text="🏠  Enclosures")
        self._nb.add(self._tab_resources(),    text="🛒  Resources")
        self._nb.add(self._tab_finances(),     text="💰  Finances")
        self._nb.add(self._tab_eventlog(),     text="📋  Event Log")
        self._nb.add(self._tab_achievements(), text="🏅  Achievements")

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
        _btn(foot, "🏅 Achievements", self._do_achievements,
             bg="#7b1fa2").pack(side="left", padx=10)
        _btn(foot, "❓ How to Play", self._do_help,
             bg=_BTN_BLU).pack(side="left", padx=4)
        _btn(foot, "Quit", self._do_quit, bg="#444").pack(side="right", padx=14)
        self._score_var = tk.StringVar(value="Score: 0")
        tk.Label(foot, textvariable=self._score_var, bg=_ACCENT,
                 fg=_GOLD, font=FONT_HEAD).pack(side="right", padx=20)
        # Personal-best label
        self._best_var = tk.StringVar(value="")
        tk.Label(foot, textvariable=self._best_var, bg=_ACCENT,
                 fg=_GREEN, font=FONT_SMALL).pack(side="right", padx=8)

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

        # Daily challenge card (inside welfare_card, below the bars)
        sep = tk.Frame(welfare_card, bg=_ACCENT, height=1)
        sep.pack(fill="x", pady=(12, 8))
        tk.Label(welfare_card, text="🎯  Today's Challenge",
                 bg=_CARD, fg=_GOLD, font=FONT_HEAD).pack(anchor="w")
        self._challenge_icon_var  = tk.StringVar(value="—")
        self._challenge_title_var = tk.StringVar(value="Advance the day to get a challenge!")
        self._challenge_desc_var  = tk.StringVar(value="")
        self._challenge_status_var= tk.StringVar(value="")
        ch_row = tk.Frame(welfare_card, bg=_CARD)
        ch_row.pack(fill="x", pady=(4, 0))
        tk.Label(ch_row, textvariable=self._challenge_icon_var,
                 bg=_CARD, fg=_GOLD, font=("Helvetica", 18)).pack(side="left", padx=(0, 8))
        right = tk.Frame(ch_row, bg=_CARD)
        right.pack(side="left", fill="x", expand=True)
        tk.Label(right, textvariable=self._challenge_title_var,
                 bg=_CARD, fg=_FG, font=FONT_BOLD9, anchor="w").pack(anchor="w")
        tk.Label(right, textvariable=self._challenge_desc_var,
                 bg=_CARD, fg=_FG2, font=FONT_SMALL, anchor="w",
                 wraplength=300).pack(anchor="w")
        self._challenge_status_lbl = tk.Label(
            welfare_card, textvariable=self._challenge_status_var,
            bg=_CARD, font=FONT_BOLD9, anchor="w")
        self._challenge_status_lbl.pack(anchor="w", pady=(4, 0))

        # Stats + streak card
        right_col = tk.Frame(mid, bg=_BG)
        right_col.pack(side="left", fill="both", expand=True)

        stats_card = tk.Frame(right_col, bg=_CARD, padx=14, pady=14)
        stats_card.pack(fill="both", expand=True, pady=(0, 6))
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

        # Streak / personal best card
        streak_card = tk.Frame(right_col, bg=_CARD, padx=14, pady=10)
        streak_card.pack(fill="x")
        tk.Label(streak_card, text="🔥  Streak & Records",
                 bg=_CARD, fg=_GOLD, font=FONT_HEAD).pack(anchor="w", pady=(0, 6))
        self._dash_streak_var = tk.StringVar(value="No-death streak: 0 days")
        self._dash_best_var   = tk.StringVar(value="Personal best: 0")
        tk.Label(streak_card, textvariable=self._dash_streak_var,
                 bg=_CARD, fg=_CYAN, font=FONT_BOLD9).pack(anchor="w")
        tk.Label(streak_card, textvariable=self._dash_best_var,
                 bg=_CARD, fg=_GOLD, font=FONT_BOLD9).pack(anchor="w")

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
    # Tab: Achievements
    # ==================================================================

    def _tab_achievements(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        # Header row
        hdr = tk.Frame(frame, bg=_CARD, padx=14, pady=10)
        hdr.pack(fill="x", padx=14, pady=(14, 6))
        tk.Label(hdr, text="🏅  Achievements Gallery",
                 bg=_CARD, fg=_GOLD, font=FONT_TITLE).pack(side="left")
        self._ach_progress_var = tk.StringVar(value="0 / 0 unlocked")
        tk.Label(hdr, textvariable=self._ach_progress_var,
                 bg=_CARD, fg=_FG2, font=FONT_SMALL).pack(side="right")

        # Scrollable grid of achievement cards
        container = tk.Frame(frame, bg=_BG)
        container.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        canvas = tk.Canvas(container, bg=_BG, highlightthickness=0)
        vsb    = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._ach_inner = tk.Frame(canvas, bg=_BG)
        self._ach_canvas_win = canvas.create_window((0, 0), window=self._ach_inner, anchor="nw")
        self._ach_inner.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._ach_canvas_win, width=e.width))
        self._ach_canvas = canvas

        # Challenge history panel
        hist_frame = tk.Frame(frame, bg=_CARD, padx=14, pady=10)
        hist_frame.pack(fill="x", padx=14, pady=(0, 10))
        tk.Label(hist_frame, text="🎯  Challenge History",
                 bg=_CARD, fg=_GOLD, font=FONT_HEAD).pack(anchor="w", pady=(0, 6))
        ch_cols = ("Day", "Challenge", "Reward", "Result")
        self._ch_hist_tree = ttk.Treeview(
            hist_frame, columns=ch_cols, show="headings", height=5)
        for col, w in zip(ch_cols, (50, 200, 80, 80)):
            self._ch_hist_tree.heading(col, text=col)
            self._ch_hist_tree.column(col, width=w, anchor="center")
        self._ch_hist_tree.tag_configure("win",  foreground=_GREEN)
        self._ch_hist_tree.tag_configure("fail", foreground=_RED)
        self._ch_hist_tree.pack(fill="x")

        self._update_achievements_tab()
        return frame

    def _update_achievements_tab(self) -> None:
        """Refresh the achievement cards and challenge history."""
        unlocked = self._achievements.unlocked_keys
        total    = len(ACHIEVEMENTS)
        count    = len(unlocked)
        self._ach_progress_var.set(
            f"{count} / {total} unlocked  ({round(count/total*100) if total else 0}%)"
        )

        # Rebuild cards
        for w in self._ach_inner.winfo_children():
            w.destroy()

        cols = 4
        for idx, ach in enumerate(ACHIEVEMENTS):
            row_n, col_n = divmod(idx, cols)
            locked  = ach.key not in unlocked
            card_bg = _PANEL if not locked else _CARD
            fg_main = _FG   if not locked else _FG2

            card = tk.Frame(self._ach_inner, bg=card_bg, padx=10, pady=8,
                            highlightbackground=(_GOLD if not locked else "#2a2a4a"),
                            highlightthickness=1)
            card.grid(row=row_n, column=col_n, padx=5, pady=4, sticky="nsew")
            self._ach_inner.columnconfigure(col_n, weight=1)

            top = tk.Frame(card, bg=card_bg)
            top.pack(fill="x")
            tk.Label(top, text=ach.icon if not locked else "🔒",
                     bg=card_bg, fg=_GOLD if not locked else _FG2,
                     font=("Helvetica", 16)).pack(side="left", padx=(0, 6))
            tk.Label(top, text=ach.title, bg=card_bg,
                     fg=fg_main, font=FONT_BOLD9).pack(side="left", anchor="w")
            tk.Label(card, text=ach.description, bg=card_bg,
                     fg=_FG2, font=FONT_SMALL,
                     wraplength=160, justify="left").pack(anchor="w")
            if ach.reward > 0:
                tk.Label(card, text=f"+${ach.reward:,.0f} AUD",
                         bg=card_bg,
                         fg=(_GREEN if not locked else _FG2),
                         font=FONT_SMALL).pack(anchor="w")

        # Challenge history
        for item in self._ch_hist_tree.get_children():
            self._ch_hist_tree.delete(item)
        for ch in self._challenges.recent_history:
            result = "✅ Done" if ch.completed else "❌ Failed"
            tag    = "win" if ch.completed else "fail"
            self._ch_hist_tree.insert(
                "", "end",
                values=(ch.day, ch.title, f"${ch.reward:,.0f}", result),
                tags=(tag,))

    # ==================================================================
    # Refresh logic
    # ==================================================================

    def _schedule_refresh(self) -> None:
        self._update_header()
        self._update_dashboard()
        self._root.after(self._REFRESH_MS, self._schedule_refresh)

    def _schedule_ticker(self) -> None:
        """Scroll one character of the ticker message."""
        if not self._ticker_msgs:
            self._root.after(self._TICKER_DELAY * 10, self._schedule_ticker)
            return
        full = "  ◆  ".join(self._ticker_msgs)
        # Rotate by _ticker_pos
        idx = self._ticker_pos % len(full)
        display = full[idx:] + "   " + full[:idx]
        # Show only up to 80 chars so it fits
        self._ticker_var.set(display[:self._TICKER_WIDTH])
        self._ticker_pos = (self._ticker_pos + 1) % len(full)
        self._root.after(self._TICKER_DELAY, self._schedule_ticker)

    def _push_ticker(self, msg: str) -> None:
        """Add a new message to the news ticker (keeps last 8)."""
        self._ticker_msgs.append(msg)
        if len(self._ticker_msgs) > 8:
            self._ticker_msgs.pop(0)

    def _refresh(self) -> None:
        self._update_header()
        self._update_dashboard()
        self._update_animals_tree()
        self._update_enclosures_tree()
        self._update_resources_bars()
        self._update_finances()
        self._update_eventlog()
        self._update_achievements_tab()

    def _update_header(self) -> None:
        zoo = self._zoo
        self._status_var.set(
            f"Day {zoo.day}  ·  "
            f"Balance: ${zoo.finance.get_balance():,.2f} AUD  ·  "
            f"Visitors today: {len(zoo.daily_visitors)}  ·  "
            f"Animals: {len(zoo.get_alive_animals())}"
        )
        self._score_var.set(f"Score: {zoo.score}")
        self._stars_var.set(f"  {_stars(zoo.score)}")
        pb = self._best_score
        if pb > 0:
            self._best_var.set(f"Best: {pb}")

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

        # Streak + personal best
        streak = self._achievements.stats.get("no_death_streak", 0)
        self._dash_streak_var.set(
            f"🔥 No-death streak: {streak} day{'s' if streak != 1 else ''}"
            + (" 🏆" if streak >= 10 else "")
        )
        self._dash_best_var.set(f"⭐ Personal best score: {self._best_score}")

        # Challenge display
        ch = self._current_challenge
        if ch is None and self._challenge_result is None:
            self._challenge_icon_var.set("—")
            self._challenge_title_var.set("Advance the day to get a challenge!")
            self._challenge_desc_var.set("")
            self._challenge_status_var.set("")
        elif ch is not None:
            self._challenge_icon_var.set(ch.icon)
            self._challenge_title_var.set(ch.title)
            self._challenge_desc_var.set(ch.description + f"  |  Reward: +${ch.reward:,.0f} AUD")
            self._challenge_status_var.set("⏳ In progress — advance the day to complete!")
            self._challenge_status_lbl.config(fg=_YELLOW)
        if self._challenge_result is not None:
            success, reward = self._challenge_result
            if success:
                self._challenge_status_var.set(
                    f"✅ Completed! +${reward:,.0f} AUD earned!"
                )
                self._challenge_status_lbl.config(fg=_GREEN)
            else:
                self._challenge_status_var.set("❌ Challenge failed. Try again tomorrow!")
                self._challenge_status_lbl.config(fg=_RED)

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
        # 1) Generate today's challenge BEFORE ticking (so description is visible)
        if self._current_challenge is None:
            self._current_challenge = self._challenges.generate_for_day(
                self._zoo.day + 1
            )

        prev_score    = self._zoo.score
        alive_before  = set(a.name for a in self._zoo.get_alive_animals())

        report = self._loop.tick()

        # 2) Compute day summary for challenge/achievement evaluation
        alive_after  = set(a.name for a in self._zoo.get_alive_animals())
        deaths_today = len(alive_before - alive_after)
        today_vis    = len(self._zoo.daily_visitors)
        today_rev    = today_vis * self._zoo.ticket_price
        score_inc    = self._zoo.score > prev_score

        day_summary = {
            "deaths_today":    deaths_today,
            "today_visitors":  today_vis,
            "today_revenue":   today_rev,
            "score_increased": score_inc,
        }

        # 3) Update achievement stats
        self._achievements.record_today_visitors(today_vis)
        self._achievements.update_daily_streaks(self._zoo)
        self._achievements.update_no_death_streak(deaths_today)

        # 4) Evaluate daily challenge
        ch_success, ch_reward = self._challenges.evaluate_current(
            self._zoo, day_summary
        )
        self._challenge_result = (ch_success, ch_reward)
        if ch_success and ch_reward > 0:
            self._zoo.finance.add_income(
                ch_reward, "challenge", f"Challenge reward: Day {self._zoo.day}"
            )
            self._push_ticker(
                f"🎯 Challenge COMPLETE! +${ch_reward:,.0f} AUD earned!"
            )

        # 5) Check achievements — fire toasts for newly unlocked ones
        newly = self._achievements.check_all(self._zoo)
        for ach in newly:
            if ach.reward > 0:
                self._zoo.finance.add_income(
                    ach.reward, "achievement",
                    f"Achievement reward: {ach.title}"
                )
            msg = f"{ach.icon}  Achievement unlocked: {ach.title}!"
            _Toast.show(self._root, msg, colour=_GOLD)
            self._push_ticker(msg)

        # 6) No-death streak bonus (every 5 clean days)
        streak = self._achievements.stats.get("no_death_streak", 0)
        if streak > 0 and streak % 5 == 0:
            bonus = streak * 50.0
            self._zoo.finance.add_income(
                bonus, "streak_bonus",
                f"{streak}-day no-death streak bonus"
            )
            _Toast.show(
                self._root,
                f"🔥 {streak}-day streak bonus! +${bonus:,.0f} AUD",
                colour=_CYAN,
            )
            self._push_ticker(f"🔥 {streak}-day no-death streak! +${bonus:,.0f} AUD bonus!")

        # 7) Personal best tracking
        if self._zoo.score > self._best_score:
            old_best = self._best_score
            self._best_score = self._zoo.score
            if old_best > 0:
                _Toast.show(
                    self._root,
                    f"⭐ New personal best: {self._best_score}!",
                    colour=_YELLOW,
                )
                self._push_ticker(f"⭐ New personal best score: {self._best_score}!")

        # 8) Generate tomorrow's challenge ready for display
        self._current_challenge = self._challenges.generate_for_day(
            self._zoo.day + 1
        )

        # 9) Push random-event / report highlights to ticker
        if "heatwave" in report.lower():
            self._push_ticker("🌡️ Heatwave hit the zoo! Medicate animals!")
        elif "celebration" in report.lower():
            self._push_ticker("🎉 Zoo Celebration! Crowds and donations!")
        elif "escape" in report.lower():
            self._push_ticker("🚨 Animal escaped! Recapture costs incurred.")
        elif "outbreak" in report.lower():
            self._push_ticker("🦠 Disease Outbreak! Check your animals now!")
        elif "donation" in report.lower():
            self._push_ticker("💝 Generous donation received!")
        elif "baby" in report.lower() or "born" in report.lower():
            self._push_ticker("🍼 New baby born at OzZoo!")

        self._refresh()

        # 10) Accumulate report lines into event history
        day = self._zoo.day
        self._event_lines.append(f"{'─' * 55}")
        self._event_lines.append(f"📅  Day {day} — Daily Report")
        self._event_lines.append(f"{'─' * 55}")
        for line in report.split("\n"):
            stripped = line.strip()
            if stripped and stripped not in ("─" * 50, "─" * 55):
                self._event_lines.append(line)
        for entry in self._zoo.event_logger.get_all_entries():
            ts  = entry["timestamp"][:10]
            et  = entry["event_type"].upper()
            msg = entry["data"].get("message") or str(entry["data"])
            self._event_lines.append(f"[{ts}] {et}: {msg}")
        self._zoo.event_logger.clear()

        self._update_eventlog()

        # 11) Daily report popup (colour-coded)
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
                 text=f"Balance: ${bal:,.2f} AUD  ·  Score: {self._zoo.score}"
                      f"  {_stars(self._zoo.score)}",
                 bg=_ACCENT, fg=_FG, font=FONT_BODY).pack()

        # Challenge result banner inside the popup
        if self._challenge_result is not None:
            success, reward = self._challenge_result
            banner_bg = "#1b4a1b" if success else "#4a1b1b"
            banner_fg = _GREEN   if success else _RED
            banner_txt = (
                f"🎯 Challenge: {'✅ COMPLETE' if success else '❌ FAILED'}"
                + (f" (+${reward:,.0f} AUD)" if success else "")
            )
            banner = tk.Frame(dlg, bg=banner_bg, pady=6)
            banner.pack(fill="x")
            tk.Label(banner, text=banner_txt, bg=banner_bg,
                     fg=banner_fg, font=FONT_BOLD9).pack()

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
            self._achievements.record_feed()
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
            self._achievements.record_upgrade()
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
            self._achievements.record_build()
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
            # Persist addictive-gameplay state
            data["_achievements"] = self._achievements.to_dict()
            data["_challenges"]   = self._challenges.to_dict()
            data["_best_score"]   = self._best_score
            data["_no_death_streak"] = self._achievements.stats.get("no_death_streak", 0)
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
            self._event_lines   = []
            self._best_score    = data.get("_best_score", 0)
            self._current_challenge  = None
            self._challenge_result   = None
            self._achievements.from_dict(data.get("_achievements", {}))
            self._challenges.from_dict(data.get("_challenges",   {}))
            self._refresh()
            messagebox.showinfo("Load Game", f"Game loaded from '{SAVE_FILE}'.")
        except Exception as exc:
            messagebox.showerror("Load Error", str(exc))

    def _do_achievements(self) -> None:
        """Open the Achievements gallery dialog."""
        _AchievementsDialog(self._root, self._achievements)

    def _do_help(self) -> None:
        """Open the How to Play dialog."""
        _HelpDialog(self._root)

    def _do_quit(self) -> None:
        stars = _stars(self._zoo.score)
        if messagebox.askyesno(
            "Quit OzZoo",
            f"Are you sure?\n\n"
            f"Final score: {self._zoo.score}  {stars}\n"
            f"Personal best: {self._best_score}\n"
            f"Achievements: {self._achievements.unlocked_count}/{self._achievements.total_count}",
        ):
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
