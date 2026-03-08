"""
gui.py
======
Tkinter-based graphical user interface for the OzZoo Zoo Simulation.

Launch via::

    python main.py --gui

or directly::

    python gui.py

The GUI offers the same features as the CLI:

* View and manage animals (feed, medicate, move, buy, make perform)
* Manage enclosures (view, clean, upgrade, build)
* Manage resources (food and medicine inventory, purchasing)
* Manage finances (report, ticket price, income/expense breakdown)
* Advance the simulation by one day with a detailed daily report
* Save and load game state

Design notes
------------
* Uses **only the Python standard library** (tkinter) — no third-party packages.
* The Zoo/GameLoop objects are the exact same ones used by the CLI; the GUI
  is purely a different presentation layer.
* All zoo mutations go through the same ``Zoo`` public methods, so game logic
  is untouched.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ---------------------------------------------------------------------------
# Ensure the ozzoo package directory is importable when run directly.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

from zoo import Zoo                          # noqa: E402
from game_loop import GameLoop               # noqa: E402
from patterns.factory import AnimalFactory   # noqa: E402
from finance import Finance                  # noqa: E402
from exceptions import OzZooException        # noqa: E402

SAVE_FILE = "ozzoo_save.json"

# ---------------------------------------------------------------------------
# Colour palette — dark Australian-outback theme
# ---------------------------------------------------------------------------
_BG      = "#1c1c2e"   # deep navy background
_PANEL   = "#16213e"   # slightly lighter panels / text-areas
_ACCENT  = "#0f3460"   # mid-blue accent (header / footer)
_GOLD    = "#f5a623"   # gold headings & highlights
_FG      = "#dde1e7"   # main foreground text
_BTN_RED = "#e94560"   # action / destructive buttons
_BTN_BLU = "#0f3460"   # neutral / secondary buttons
_GREEN   = "#4caf50"
_ORANGE  = "#ff9800"
_RED     = "#f44336"
_TROUGH  = "#2a2a4a"   # scrollbar trough


def _health_color(value: int) -> str:
    """Map a 0-100 value (health, happiness, cleanliness) to a colour."""
    if value >= 70:
        return _GREEN
    if value >= 30:
        return _ORANGE
    return _RED


# ---------------------------------------------------------------------------
# Reusable widget helpers
# ---------------------------------------------------------------------------

def _btn(parent: tk.Widget, text: str, cmd, bg: str = _BTN_BLU, **kw) -> tk.Button:
    """Create a styled button."""
    return tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=bg,
        fg=_FG,
        activebackground=_GOLD,
        activeforeground="#000",
        relief="flat",
        padx=10,
        pady=4,
        font=("Helvetica", 9, "bold"),
        cursor="hand2",
        **kw,
    )


def _text_area(parent: tk.Widget, **kw) -> tk.Text:
    """Create a styled Text widget (disabled by default)."""
    kw.setdefault("state", "disabled")
    return tk.Text(
        parent,
        bg=_PANEL,
        fg=_FG,
        insertbackground=_FG,
        relief="flat",
        font=("Courier", 9),
        **kw,
    )


def _write_text(widget: tk.Text, content: str) -> None:
    """Replace all text in a disabled Text widget."""
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.insert("end", content)
    widget.configure(state="disabled")


# ---------------------------------------------------------------------------
# Modal dialog classes
# ---------------------------------------------------------------------------

class _BuyAnimalDialog(tk.Toplevel):
    """Modal dialog for purchasing a new animal."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.title("Buy New Animal")
        self.configure(bg=_BG)
        self.resizable(False, False)
        self.grab_set()
        self.result: Optional[tuple] = None  # (species, name, age)

        species_list = AnimalFactory.supported_species()

        tk.Label(self, text="Buy New Animal 🐾", bg=_BG, fg=_GOLD,
            row=1, column=0, sticky="e", padx=10, pady=4)
        self._species_var = tk.StringVar(value=species_list[0])
        ttk.Combobox(self, textvariable=self._species_var, values=species_list,
                     state="readonly", width=20).grid(row=1, column=1, padx=10, pady=4)

        tk.Label(self, text="Name:", bg=_BG, fg=_FG).grid(
            row=2, column=0, sticky="e", padx=10, pady=4)
        self._name_var = tk.StringVar()
        tk.Entry(self, textvariable=self._name_var, bg=_PANEL, fg=_FG,
                 insertbackground=_FG, width=22).grid(row=2, column=1, padx=10, pady=4)

        tk.Label(self, text="Age (years):", bg=_BG, fg=_FG).grid(
            row=3, column=0, sticky="e", padx=10, pady=4)
        self._age_var = tk.IntVar(value=2)
        tk.Spinbox(self, from_=0, to=30, textvariable=self._age_var,
                   bg=_PANEL, fg=_FG, width=8).grid(
            row=3, column=1, sticky="w", padx=10, pady=4)

        btn_row = tk.Frame(self, bg=_BG)
        btn_row.grid(row=4, column=0, columnspan=2, pady=14)
        _btn(btn_row, "Buy", self._ok, bg=_BTN_RED).pack(side="left", padx=8)
        _btn(btn_row, "Cancel", self.destroy).pack(side="left", padx=8)

        self.wait_window()

    def _ok(self) -> None:
        name = self._name_var.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Please enter an animal name.",
                                 parent=self)
            return
        self.result = (self._species_var.get(), name, self._age_var.get())
        self.destroy()


class _MoveAnimalDialog(tk.Toplevel):
    """Modal dialog for moving an animal to a different enclosure."""

    def __init__(self, parent: tk.Widget, zoo: Zoo) -> None:
        super().__init__(parent)
        self.title("Move Animal")
        self.configure(bg=_BG)
        self.resizable(False, False)
        self.grab_set()
        self.result: Optional[tuple] = None  # (animal_name, enclosure_id)

        animal_names = [a.name for a in zoo.get_alive_animals()]
        enc_labels   = [f"{e.enclosure_id} — {e.name} ({e.habitat_type})"
                        for e in zoo.enclosures]
        self._enc_ids     = [e.enclosure_id for e in zoo.enclosures]
        self._enc_labels  = enc_labels

        tk.Label(self, text="Move Animal 🏠", bg=_BG, fg=_GOLD,
                 font=("Helvetica", 13, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(14, 8), padx=20)

        tk.Label(self, text="Animal:", bg=_BG, fg=_FG).grid(
            row=1, column=0, sticky="e", padx=10, pady=4)
        self._animal_var = tk.StringVar(value=animal_names[0] if animal_names else "")
        ttk.Combobox(self, textvariable=self._animal_var, values=animal_names,
                     state="readonly", width=24).grid(row=1, column=1, padx=10, pady=4)

        tk.Label(self, text="To Enclosure:", bg=_BG, fg=_FG).grid(
            row=2, column=0, sticky="e", padx=10, pady=4)
        self._enc_var = tk.StringVar(value=enc_labels[0] if enc_labels else "")
        ttk.Combobox(self, textvariable=self._enc_var, values=enc_labels,
                     state="readonly", width=30).grid(row=2, column=1, padx=10, pady=4)

        btn_row = tk.Frame(self, bg=_BG)
        btn_row.grid(row=3, column=0, columnspan=2, pady=14)
        _btn(btn_row, "Move", self._ok, bg=_BTN_RED).pack(side="left", padx=8)
        _btn(btn_row, "Cancel", self.destroy).pack(side="left", padx=8)

        self.wait_window()

    def _ok(self) -> None:
        animal_name = self._animal_var.get()
        enc_label   = self._enc_var.get()
        if not animal_name or not enc_label:
            return
        idx    = self._enc_labels.index(enc_label) if enc_label in self._enc_labels else 0
        enc_id = self._enc_ids[idx]
        self.result = (animal_name, enc_id)
        self.destroy()


class _BuildEnclosureDialog(tk.Toplevel):
    """Modal dialog for building a new enclosure."""

    HABITAT_TYPES = ["Savannah", "Arctic", "Wetlands", "Forest", "Desert", "Ocean"]

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.title("Build New Enclosure")
        self.configure(bg=_BG)
        self.resizable(False, False)
        self.grab_set()
        self.result: Optional[tuple] = None  # (name, habitat, capacity, area)

        tk.Label(self, text="Build New Enclosure 🏗️", bg=_BG, fg=_GOLD,
                 font=("Helvetica", 13, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(14, 8), padx=20)

        tk.Label(self, text="Name:", bg=_BG, fg=_FG).grid(
            row=1, column=0, sticky="e", padx=10, pady=4)
        self._name_var = tk.StringVar()
        tk.Entry(self, textvariable=self._name_var, bg=_PANEL, fg=_FG,
                 insertbackground=_FG, width=22).grid(row=1, column=1, padx=10, pady=4)

        tk.Label(self, text="Habitat Type:", bg=_BG, fg=_FG).grid(
            row=2, column=0, sticky="e", padx=10, pady=4)
        self._habitat_var = tk.StringVar(value=self.HABITAT_TYPES[0])
        ttk.Combobox(self, textvariable=self._habitat_var, values=self.HABITAT_TYPES,
                     state="readonly", width=20).grid(row=2, column=1, padx=10, pady=4)

        tk.Label(self, text="Max Capacity:", bg=_BG, fg=_FG).grid(
            row=3, column=0, sticky="e", padx=10, pady=4)
        self._cap_var = tk.IntVar(value=5)
        tk.Spinbox(self, from_=2, to=20, textvariable=self._cap_var,
                   bg=_PANEL, fg=_FG, width=8).grid(
            row=3, column=1, sticky="w", padx=10, pady=4)

        tk.Label(self, text="Area (m²):", bg=_BG, fg=_FG).grid(
            row=4, column=0, sticky="e", padx=10, pady=4)
        self._area_var = tk.DoubleVar(value=200.0)
        tk.Spinbox(self, from_=50, to=2000, increment=50,
                   textvariable=self._area_var, bg=_PANEL, fg=_FG, width=8).grid(
            row=4, column=1, sticky="w", padx=10, pady=4)

        btn_row = tk.Frame(self, bg=_BG)
        btn_row.grid(row=5, column=0, columnspan=2, pady=14)
        _btn(btn_row, "Build", self._ok, bg=_BTN_RED).pack(side="left", padx=8)
        _btn(btn_row, "Cancel", self.destroy).pack(side="left", padx=8)

        self.wait_window()

    def _ok(self) -> None:
        name = self._name_var.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Please enter an enclosure name.",
                                 parent=self)
            return
        self.result = (name, self._habitat_var.get(),
                       self._cap_var.get(), self._area_var.get())
        self.destroy()


# ---------------------------------------------------------------------------
# Main GUI application
# ---------------------------------------------------------------------------

class OzZooGUI:
    """
    Tkinter graphical interface for the OzZoo Zoo Simulation.

    Parameters
    ----------
    root : tk.Tk
        The Tk root window passed in from :func:`run_gui`.
    """

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._zoo  = Zoo()
        self._loop = GameLoop(self._zoo)

        root.title("🦘  OzZoo — Australian Zoo Management")
        root.configure(bg=_BG)
        root.minsize(940, 640)

        self._build_header()
        self._build_notebook()
        self._build_footer()
        self._refresh()

    # ------------------------------------------------------------------
    # Layout construction
    # ------------------------------------------------------------------

    def _build_header(self) -> None:
        """Top status bar: zoo name + live stats."""
        hdr = tk.Frame(self._root, bg=_ACCENT, pady=8)
        hdr.pack(fill="x")

        tk.Label(hdr, text="🦘  OzZoo — Australian Zoo Management  🦘",
                 bg=_ACCENT, fg=_GOLD, font=("Helvetica", 16, "bold")).pack()

        self._status_var = tk.StringVar()
        tk.Label(hdr, textvariable=self._status_var, bg=_ACCENT, fg=_FG,
                 font=("Helvetica", 10)).pack()

    def _build_notebook(self) -> None:
        """Central tabbed notebook."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",     background=_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=_ACCENT, foreground=_FG,
                        padding=[14, 6], font=("Helvetica", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", _GOLD)],
                  foreground=[("selected", "#000")])
        style.configure("Treeview", background=_PANEL, foreground=_FG,
                        fieldbackground=_PANEL, rowheight=23)
        style.configure("Treeview.Heading", background=_ACCENT, foreground=_GOLD,
                        font=("Helvetica", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", _BTN_RED)],
                  foreground=[("selected", "#fff")])
        style.configure("TScrollbar", background=_PANEL, troughcolor=_TROUGH)

        nb = ttk.Notebook(self._root)
        nb.pack(fill="both", expand=True, padx=8, pady=6)

        nb.add(self._tab_animals(),    text="🐾  Animals")
        nb.add(self._tab_enclosures(), text="🏠  Enclosures")
        nb.add(self._tab_resources(),  text="🛒  Resources")
        nb.add(self._tab_finances(),   text="💰  Finances")
        nb.add(self._tab_eventlog(),   text="📋  Event Log")

    def _build_footer(self) -> None:
        """Bottom action bar with game-wide controls."""
        foot = tk.Frame(self._root, bg=_ACCENT, pady=8)
        foot.pack(fill="x", side="bottom")

        _btn(foot, "  Advance Day  ➜  ", self._do_advance_day,
             bg=_BTN_RED).pack(side="left", padx=12)
        _btn(foot, "Save Game",  self._do_save).pack(side="left", padx=4)
        _btn(foot, "Load Game",  self._do_load).pack(side="left", padx=4)
        _btn(foot, "Quit", self._do_quit, bg="#444").pack(side="right", padx=12)

    # ------------------------------------------------------------------
    # Tab builders
    # ------------------------------------------------------------------

    def _tab_animals(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)  # parent will be the Notebook
        cols  = ("Name", "Species", "Age", "Health", "Hunger", "Happiness")
        self._anim_tree = ttk.Treeview(frame, columns=cols, show="headings",
                                       selectmode="browse", height=15)
        widths = (120, 140, 55, 80, 80, 90)
        for col, w in zip(cols, widths):
            self._anim_tree.heading(col, text=col)
            self._anim_tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self._anim_tree.yview)
        self._anim_tree.configure(yscrollcommand=vsb.set)
        self._anim_tree.pack(side="left", fill="both", expand=True,
                             padx=(8, 0), pady=8)
        vsb.pack(side="left", fill="y", pady=8)

        sf = tk.Frame(frame, bg=_BG)
        sf.pack(side="right", fill="y", padx=10, pady=8)
        for label, cmd in [
            ("Feed Selected",     self._do_feed_animal),
            ("Medicate Selected", self._do_medicate_animal),
            ("Make Perform",      self._do_perform_animal),
            ("Move to Enclosure", self._do_move_animal),
            ("Buy New Animal",    self._do_buy_animal),
        ]:
            _btn(sf, label, cmd).pack(fill="x", pady=4)

        return frame

    def _tab_enclosures(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)
        cols  = ("ID", "Name", "Habitat", "Animals", "Capacity",
                 "Cleanliness", "Level")
        self._enc_tree = ttk.Treeview(frame, columns=cols, show="headings",
                                      selectmode="browse", height=15)
        widths = (80, 160, 100, 70, 80, 110, 60)
        for col, w in zip(cols, widths):
            self._enc_tree.heading(col, text=col)
            self._enc_tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self._enc_tree.yview)
        self._enc_tree.configure(yscrollcommand=vsb.set)
        self._enc_tree.pack(side="left", fill="both", expand=True,
                            padx=(8, 0), pady=8)
        vsb.pack(side="left", fill="y", pady=8)

        sf = tk.Frame(frame, bg=_BG)
        sf.pack(side="right", fill="y", padx=10, pady=8)
        for label, cmd in [
            ("Clean Selected",      self._do_clean_enclosure),
            ("Upgrade Selected",    self._do_upgrade_enclosure),
            ("Build New Enclosure", self._do_build_enclosure),
        ]:
            _btn(sf, label, cmd).pack(fill="x", pady=4)

        return frame

    def _tab_resources(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        food_lf = tk.LabelFrame(frame, text=" 🌿  Food Inventory ",
                                bg=_BG, fg=_GOLD, font=("Helvetica", 10, "bold"),
                                labelanchor="n")
        food_lf.pack(fill="both", expand=True, padx=14, pady=(14, 6))
        self._food_txt = _text_area(food_lf, height=8)
        self._food_txt.pack(fill="both", expand=True, padx=6, pady=6)
        _btn(food_lf, "Buy Food", self._do_buy_food,
             bg=_BTN_RED).pack(pady=(0, 8))

        med_lf = tk.LabelFrame(frame, text=" 💊  Medicine Inventory ",
                               bg=_BG, fg=_GOLD, font=("Helvetica", 10, "bold"),
                               labelanchor="n")
        med_lf.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        self._med_txt = _text_area(med_lf, height=8)
        self._med_txt.pack(fill="both", expand=True, padx=6, pady=6)
        _btn(med_lf, "Buy Medicine", self._do_buy_medicine,
             bg=_BTN_RED).pack(pady=(0, 8))

        return frame

    def _tab_finances(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        self._fin_txt = _text_area(frame)
        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self._fin_txt.yview)
        self._fin_txt.configure(yscrollcommand=vsb.set)
        self._fin_txt.pack(side="left", fill="both", expand=True,
                           padx=(8, 0), pady=8)
        vsb.pack(side="left", fill="y", pady=8)

        sf = tk.Frame(frame, bg=_BG)
        sf.pack(side="right", fill="y", padx=10, pady=8)
        for label, cmd in [
            ("Set Ticket Price",      self._do_set_ticket_price),
            ("Income by Source",      self._do_income_sources),
            ("Expenses by Category",  self._do_expense_categories),
        ]:
            _btn(sf, label, cmd).pack(fill="x", pady=4)

        return frame

    def _tab_eventlog(self) -> tk.Frame:
        frame = tk.Frame(self._root, bg=_BG)

        self._log_txt = _text_area(frame)
        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self._log_txt.yview)
        self._log_txt.configure(yscrollcommand=vsb.set)
        self._log_txt.pack(side="left", fill="both", expand=True,
                           padx=(8, 0), pady=8)
        vsb.pack(side="left", fill="y", pady=8)

        return frame

    # ------------------------------------------------------------------
    # Refresh / update helpers
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        """Redraw all widgets from the current Zoo state."""
        self._update_header()
        self._update_animals_tree()
        self._update_enclosures_tree()
        self._update_resources_text()
        self._update_finances_text()
        self._update_eventlog_text()

    def _update_header(self) -> None:
        zoo = self._zoo
        self._status_var.set(
            f"Day: {zoo.day}  │  "
            f"💰 ${zoo.finance.get_balance():,.2f} AUD  │  "
            f"👥 Visitors: {len(zoo.daily_visitors)}  │  "
            f"🏆 Score: {zoo.score}"
        )

    def _update_animals_tree(self) -> None:
        tree = self._anim_tree
        # Remember selection by name
        focused = tree.focus()
        sel_name = tree.item(focused, "values")[0] if focused else None
        for item in tree.get_children():
            tree.delete(item)

        for a in self._zoo.get_alive_animals():
            color = _health_color(a.health)
            tag   = f"h_{a.name}"
            tree.insert("", "end",
                        values=(a.name, a.species, a.age,
                                a.health, a.hunger, a.happiness),
                        tags=(tag,))
            tree.tag_configure(tag, foreground=color)

        # Restore selection
        if sel_name:
            for item in tree.get_children():
                if tree.item(item, "values")[0] == sel_name:
                    tree.focus(item)
                    tree.selection_set(item)
                    break

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

    def _update_resources_text(self) -> None:
        _write_text(self._food_txt, self._zoo.food_inventory.report())
        _write_text(self._med_txt,  self._zoo.medicine_inventory.report())

    def _update_finances_text(self) -> None:
        _write_text(self._fin_txt, self._zoo.finance.get_report())

    def _update_eventlog_text(self) -> None:
        entries = self._zoo.event_logger.get_recent(60)
        content = "\n".join(entries) if entries else "(No events logged yet.)"
        _write_text(self._log_txt, content)
        self._log_txt.configure(state="normal")
        self._log_txt.see("end")
        self._log_txt.configure(state="disabled")

    # ------------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _do_advance_day(self) -> None:
        report = self._loop.tick()
        self._refresh()
        # Show the daily report in a scrollable popup
        dlg = tk.Toplevel(self._root)
        dlg.title(f"Day {self._zoo.day} — Daily Report")
        dlg.configure(bg=_BG)
        dlg.grab_set()

        txt = _text_area(dlg, width=62, height=26)
        txt.configure(state="normal")
        txt.insert("end", report)
        txt.configure(state="disabled")
        vsb = ttk.Scrollbar(dlg, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        txt.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
        vsb.pack(side="left", fill="y", pady=12)

        _btn(dlg, "Close", dlg.destroy).pack(pady=(0, 10))

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
        med_types = ["antibiotic", "vitamin", "vaccine", "painkiller"]
        med = simpledialog.askstring(
            "Medicate Animal",
            f"Medicine type for {name}:\n({', '.join(med_types)})",
            initialvalue="antibiotic",
            parent=self._root,
        )
        if med is None:
            return
        try:
            msg = self._zoo.medicate_animal(name, med.strip() or "antibiotic")
            messagebox.showinfo("Medicate Animal", msg)
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
            messagebox.showinfo(f"{name} Performs",
                                f"{result or sound}\n\n{sound}")
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
            messagebox.showinfo("Clean Enclosure", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_upgrade_enclosure(self) -> None:
        enc_id = self._selected_enclosure_id()
        if enc_id is None:
            return
        try:
            msg = self._zoo.upgrade_enclosure(enc_id)
            messagebox.showinfo("Upgrade Enclosure", msg)
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
        food_types = sorted(self._zoo.food_inventory.VALID_TYPES)
        food_type = simpledialog.askstring(
            "Buy Food",
            f"Food type:\n({', '.join(food_types)})",
            initialvalue=food_types[0],
            parent=self._root,
        )
        if food_type is None:
            return
        units = simpledialog.askinteger(
            "Buy Food", "Units to purchase:",
            initialvalue=10, minvalue=1, maxvalue=500,
            parent=self._root,
        )
        if units is None:
            return
        try:
            msg = self._zoo.buy_food(food_type.strip(), units)
            messagebox.showinfo("Buy Food", msg)
        except (OzZooException, ValueError) as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_buy_medicine(self) -> None:
        med_types = sorted(self._zoo.medicine_inventory.VALID_TYPES)
        med_type = simpledialog.askstring(
            "Buy Medicine",
            f"Medicine type:\n({', '.join(med_types)})",
            initialvalue=med_types[0],
            parent=self._root,
        )
        if med_type is None:
            return
        doses = simpledialog.askinteger(
            "Buy Medicine", "Doses to purchase:",
            initialvalue=5, minvalue=1, maxvalue=200,
            parent=self._root,
        )
        if doses is None:
            return
        try:
            msg = self._zoo.buy_medicine(med_type.strip(), doses)
            messagebox.showinfo("Buy Medicine", msg)
        except (OzZooException, ValueError) as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_set_ticket_price(self) -> None:
        current = self._zoo.ticket_price
        price = simpledialog.askfloat(
            "Set Ticket Price",
            f"Current price: ${current:.2f} AUD\nNew price ($):",
            initialvalue=current,
            minvalue=0.01,
            maxvalue=500.0,
            parent=self._root,
        )
        if price is None:
            return
        try:
            msg = self._zoo.set_ticket_price(price)
            messagebox.showinfo("Ticket Price", msg)
        except OzZooException as exc:
            messagebox.showerror("Error", str(exc))
        self._refresh()

    def _do_income_sources(self) -> None:
        sources = self._zoo.finance.get_income_by_source()
        if not sources:
            messagebox.showinfo("Income by Source", "No income recorded yet.")
            return
        lines = ["Income by Source:", ""]
        for src, total in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {src:<22}  ${total:>12,.2f} AUD")
        messagebox.showinfo("Income by Source", "\n".join(lines))

    def _do_expense_categories(self) -> None:
        cats = self._zoo.finance.get_expenses_by_category()
        if not cats:
            messagebox.showinfo("Expenses by Category", "No expenses recorded yet.")
            return
        lines = ["Expenses by Category:", ""]
        for cat, total in sorted(cats.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {cat:<22}  ${total:>12,.2f} AUD")
        messagebox.showinfo("Expenses by Category", "\n".join(lines))

    def _do_save(self) -> None:
        try:
            data = self._zoo.to_dict()
            with open(SAVE_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            messagebox.showinfo("Save Game", f"✅ Game saved to '{SAVE_FILE}'.")
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

            self._refresh()
            messagebox.showinfo("Load Game", f"✅ Game loaded from '{SAVE_FILE}'.")
        except Exception as exc:
            messagebox.showerror("Load Error", str(exc))

    def _do_quit(self) -> None:
        if messagebox.askyesno("Quit", "Are you sure you want to quit OzZoo?"):
            self._root.quit()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_gui() -> None:
    """Create the Tk root window and start the OzZoo GUI."""
    root = tk.Tk()
    OzZooGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
