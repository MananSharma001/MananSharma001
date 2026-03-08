"""
cli.py
======
Interactive Command-Line Interface for the OzZoo simulation.

Run via ``python main.py``.

Menu structure
--------------
[1]  View Zoo Status
[2]  Manage Animals
[3]  Manage Enclosures
[4]  Manage Resources
[5]  Manage Finances
[6]  Advance Day
[7]  View Event Log
[8]  Save Game
[9]  Load Game
[0]  Quit
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

from zoo import Zoo
from game_loop import GameLoop
from patterns.factory import AnimalFactory
from exceptions import (
    OzZooException,
    InsufficientFundsError,
    InsufficientFoodError,
    AnimalNotFoundError,
    InvalidActionError,
    HabitatCapacityExceededError,
    IncompatibleSpeciesError,
)

SAVE_FILE = "ozzoo_save.json"
SEP = "=" * 55


def _header(text: str) -> None:
    """Print a formatted section header."""
    print(f"\n{SEP}")
    print(f"  {text}")
    print(SEP)


def _pause() -> None:
    """Wait for the user to press Enter."""
    input("\nPress Enter to continue...")


class CLI:
    """
    Interactive CLI for the OzZoo zoo management simulation.

    Attributes
    ----------
    _zoo : Zoo
        The active Zoo instance.
    _game_loop : GameLoop
        The game loop that wraps day-advancement.
    _running : bool
        Whether the main loop is active.
    """

    def __init__(self) -> None:
        """Initialise the CLI and create a fresh zoo."""
        self._zoo: Zoo = Zoo()
        self._game_loop: GameLoop = GameLoop(self._zoo)
        self._running: bool = True

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the interactive CLI main loop."""
        self._print_banner()
        while self._running:
            self._print_main_menu()
            choice = input("  Enter choice: ").strip()
            self._route(choice)

    # ------------------------------------------------------------------
    # Menu routing
    # ------------------------------------------------------------------

    def _route(self, choice: str) -> None:
        """Dispatch a main-menu choice to the correct handler."""
        handlers = {
            "1": self._menu_view_status,
            "2": self._menu_manage_animals,
            "3": self._menu_manage_enclosures,
            "4": self._menu_manage_resources,
            "5": self._menu_manage_finances,
            "6": self._menu_advance_day,
            "7": self._menu_view_event_log,
            "8": self._menu_save_game,
            "9": self._menu_load_game,
            "0": self._quit,
        }
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            print("  ⚠️  Invalid choice.  Please try again.")

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _print_banner(self) -> None:
        """Print the OzZoo ASCII banner."""
        print("""
╔══════════════════════════════════════════════════════╗
║         🦘  Welcome to OzZoo — Australian Zoo  🦘   ║
║      A Python OOP Zoo Simulation by MananSharma001   ║
╚══════════════════════════════════════════════════════╝
        """)

    def _print_main_menu(self) -> None:
        """Print the main menu with current zoo stats."""
        zoo = self._zoo
        balance = zoo.finance.get_balance()
        visitors = len(zoo.daily_visitors)
        print(f"\n{'─' * 55}")
        print(
            f"  🗓️  Day: {zoo.day:>3}  |  "
            f"💰 ${balance:>10,.2f} AUD  |  "
            f"👥 Visitors: {visitors}"
        )
        print(f"{'─' * 55}")
        print("""
  === OzZoo Management System ===

  [1]  View Zoo Status
  [2]  Manage Animals
  [3]  Manage Enclosures
  [4]  Manage Resources
  [5]  Manage Finances
  [6]  Advance Day  ➜
  [7]  View Event Log
  [8]  Save Game
  [9]  Load Game
  [0]  Quit
""")

    # ------------------------------------------------------------------
    # [1] View Zoo Status
    # ------------------------------------------------------------------

    def _menu_view_status(self) -> None:
        """Display an overview of the zoo."""
        print(self._zoo.get_status())
        _pause()

    # ------------------------------------------------------------------
    # [2] Manage Animals
    # ------------------------------------------------------------------

    def _menu_manage_animals(self) -> None:
        """Show the animal management sub-menu."""
        while True:
            _header("MANAGE ANIMALS")
            print("""
  [a]  View All Animals
  [b]  Buy New Animal
  [c]  Feed Animal
  [d]  Medicate Animal
  [e]  Move Animal to Enclosure
  [f]  Make Animal Perform
  [0]  Back
""")
            choice = input("  Enter choice: ").strip().lower()
            if choice == "a":
                self._view_all_animals()
            elif choice == "b":
                self._buy_animal()
            elif choice == "c":
                self._feed_animal()
            elif choice == "d":
                self._medicate_animal()
            elif choice == "e":
                self._move_animal()
            elif choice == "f":
                self._animal_perform()
            elif choice == "0":
                break
            else:
                print("  ⚠️  Invalid choice.")

    def _view_all_animals(self) -> None:
        """Print info for every animal."""
        _header("ALL ANIMALS")
        animals = self._zoo.get_alive_animals()
        if not animals:
            print("  No living animals in the zoo!")
        for animal in animals:
            print(animal.get_info())
            print()
        _pause()

    def _buy_animal(self) -> None:
        """Prompt to buy a new animal via the factory."""
        _header("BUY NEW ANIMAL")
        print(f"  Supported species: {', '.join(AnimalFactory.supported_species())}")
        species = input("  Species: ").strip()
        name = input("  Name   : ").strip()
        age_str = input("  Age    : ").strip()
        try:
            age = int(age_str) if age_str else 1
            msg = self._zoo.buy_animal(species, name, age)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _feed_animal(self) -> None:
        """Prompt to feed an animal."""
        _header("FEED ANIMAL")
        name = input("  Animal name: ").strip()
        try:
            msg = self._zoo.feed_animal(name)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _medicate_animal(self) -> None:
        """Prompt to administer medicine to an animal."""
        _header("MEDICATE ANIMAL")
        name = input("  Animal name    : ").strip()
        print("  Medicine types : antibiotic, vitamin, vaccine, painkiller")
        med = input("  Medicine type  : ").strip() or "antibiotic"
        try:
            msg = self._zoo.medicate_animal(name, med)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _move_animal(self) -> None:
        """Prompt to move an animal to a different enclosure."""
        _header("MOVE ANIMAL")
        print("  Enclosures:")
        for enc in self._zoo.enclosures:
            print(
                f"    {enc.enclosure_id}: {enc.name} "
                f"({enc.habitat_type}, {enc.animal_count}/{enc.max_capacity})"
            )
        name = input("\n  Animal name  : ").strip()
        enc_id = input("  Enclosure ID : ").strip()
        try:
            msg = self._zoo.move_animal_to_enclosure(name, enc_id)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _animal_perform(self) -> None:
        """Make an animal perform its unique behaviour."""
        _header("ANIMAL PERFORMANCE")
        name = input("  Animal name: ").strip()
        try:
            animal = self._zoo.find_animal(name)
            # Try species-specific unique behaviours first
            result: Optional[str] = None
            for method in ("jump", "swim", "run", "soar", "snap", "slither", "climb"):
                if hasattr(animal, method):
                    result = getattr(animal, method)()
                    break
            if result is None:
                result = animal.make_sound()
            print(f"\n  {result}")
            # Also play the sound
            print(f"  {animal.make_sound()}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    # ------------------------------------------------------------------
    # [3] Manage Enclosures
    # ------------------------------------------------------------------

    def _menu_manage_enclosures(self) -> None:
        """Show the enclosure management sub-menu."""
        while True:
            _header("MANAGE ENCLOSURES")
            print("""
  [a]  View All Enclosures
  [b]  Build New Enclosure
  [c]  Clean Enclosure
  [d]  Upgrade Enclosure
  [0]  Back
""")
            choice = input("  Enter choice: ").strip().lower()
            if choice == "a":
                self._view_enclosures()
            elif choice == "b":
                self._build_enclosure()
            elif choice == "c":
                self._clean_enclosure()
            elif choice == "d":
                self._upgrade_enclosure()
            elif choice == "0":
                break
            else:
                print("  ⚠️  Invalid choice.")

    def _view_enclosures(self) -> None:
        """Print a summary of all enclosures."""
        _header("ALL ENCLOSURES")
        for enc in self._zoo.enclosures:
            print(enc.get_summary())
            print()
        _pause()

    def _build_enclosure(self) -> None:
        """Prompt to build a new enclosure."""
        _header("BUILD NEW ENCLOSURE")
        habitat_types = ["Savannah", "Arctic", "Wetlands", "Forest", "Desert", "Ocean"]
        print(f"  Habitat types: {', '.join(habitat_types)}")
        name = input("  Enclosure name     : ").strip()
        habitat = input("  Habitat type       : ").strip()
        cap_str = input("  Max capacity [5]   : ").strip()
        area_str = input("  Area m² [200]      : ").strip()
        try:
            cap = int(cap_str) if cap_str else 5
            area = float(area_str) if area_str else 200.0
            msg = self._zoo.build_enclosure(name, habitat, cap, area)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _clean_enclosure(self) -> None:
        """Prompt to clean an enclosure."""
        _header("CLEAN ENCLOSURE")
        for enc in self._zoo.enclosures:
            print(f"  {enc.enclosure_id}: {enc.name} (cleanliness={enc.cleanliness})")
        enc_id = input("\n  Enclosure ID: ").strip()
        try:
            msg = self._zoo.clean_enclosure(enc_id)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _upgrade_enclosure(self) -> None:
        """Prompt to upgrade an enclosure."""
        _header("UPGRADE ENCLOSURE")
        for enc in self._zoo.enclosures:
            print(
                f"  {enc.enclosure_id}: {enc.name} "
                f"(lvl={enc.upgrade_level}, cap={enc.max_capacity}, "
                f"cost=${enc.UPGRADE_COST:.2f})"
            )
        enc_id = input("\n  Enclosure ID: ").strip()
        try:
            msg = self._zoo.upgrade_enclosure(enc_id)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    # ------------------------------------------------------------------
    # [4] Manage Resources
    # ------------------------------------------------------------------

    def _menu_manage_resources(self) -> None:
        """Show the resource management sub-menu."""
        while True:
            _header("MANAGE RESOURCES")
            print("""
  [a]  Buy Food
  [b]  Buy Medicine
  [c]  View Inventory
  [0]  Back
""")
            choice = input("  Enter choice: ").strip().lower()
            if choice == "a":
                self._buy_food()
            elif choice == "b":
                self._buy_medicine()
            elif choice == "c":
                self._view_inventory()
            elif choice == "0":
                break
            else:
                print("  ⚠️  Invalid choice.")

    def _buy_food(self) -> None:
        """Prompt to purchase food."""
        _header("BUY FOOD")
        print(self._zoo.food_inventory.report())
        food_type = input("\n  Food type : ").strip()
        units_str = input("  Units     : ").strip()
        try:
            units = int(units_str) if units_str else 10
            msg = self._zoo.buy_food(food_type, units)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _buy_medicine(self) -> None:
        """Prompt to purchase medicine."""
        _header("BUY MEDICINE")
        print(self._zoo.medicine_inventory.report())
        med_type = input("\n  Medicine type : ").strip()
        doses_str = input("  Doses         : ").strip()
        try:
            doses = int(doses_str) if doses_str else 5
            msg = self._zoo.buy_medicine(med_type, doses)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _view_inventory(self) -> None:
        """Display current food and medicine inventory."""
        _header("INVENTORY")
        print(self._zoo.food_inventory.report())
        print()
        print(self._zoo.medicine_inventory.report())
        _pause()

    # ------------------------------------------------------------------
    # [5] Manage Finances
    # ------------------------------------------------------------------

    def _menu_manage_finances(self) -> None:
        """Show the finance management sub-menu."""
        while True:
            _header("MANAGE FINANCES")
            print("""
  [a]  View Financial Report
  [b]  Set Ticket Price
  [c]  View Income by Source
  [d]  View Expenses by Category
  [0]  Back
""")
            choice = input("  Enter choice: ").strip().lower()
            if choice == "a":
                print(self._zoo.finance.get_report())
                _pause()
            elif choice == "b":
                self._set_ticket_price()
            elif choice == "c":
                self._view_income_sources()
            elif choice == "d":
                self._view_expense_categories()
            elif choice == "0":
                break
            else:
                print("  ⚠️  Invalid choice.")

    def _set_ticket_price(self) -> None:
        """Prompt to set a new ticket price."""
        _header("SET TICKET PRICE")
        print(f"  Current ticket price: ${self._zoo.ticket_price:.2f} AUD")
        price_str = input("  New price: $").strip()
        try:
            price = float(price_str)
            msg = self._zoo.set_ticket_price(price)
            print(f"\n  {msg}")
        except (OzZooException, ValueError) as e:
            print(f"\n  ❌ Error: {e}")
        _pause()

    def _view_income_sources(self) -> None:
        """Display income broken down by source."""
        _header("INCOME BY SOURCE")
        sources = self._zoo.finance.get_income_by_source()
        if not sources:
            print("  No income recorded yet.")
        else:
            for src, total in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                print(f"  {src:<20} ${total:>12,.2f} AUD")
        _pause()

    def _view_expense_categories(self) -> None:
        """Display expenses broken down by category."""
        _header("EXPENSES BY CATEGORY")
        cats = self._zoo.finance.get_expenses_by_category()
        if not cats:
            print("  No expenses recorded yet.")
        else:
            for cat, total in sorted(cats.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat:<20} ${total:>12,.2f} AUD")
        _pause()

    # ------------------------------------------------------------------
    # [6] Advance Day
    # ------------------------------------------------------------------

    def _menu_advance_day(self) -> None:
        """Advance the simulation by one day."""
        report = self._game_loop.tick()
        print(report)
        _pause()

    # ------------------------------------------------------------------
    # [7] View Event Log
    # ------------------------------------------------------------------

    def _menu_view_event_log(self) -> None:
        """Display the most recent events from the event logger."""
        _header("EVENT LOG  (last 20 entries)")
        recent = self._zoo.event_logger.get_recent(20)
        if not recent:
            print("  No events logged yet.")
        for line in recent:
            print(f"  {line}")
        _pause()

    # ------------------------------------------------------------------
    # [8] Save Game
    # ------------------------------------------------------------------

    def _menu_save_game(self) -> None:
        """Save the current game state to a JSON file."""
        _header("SAVE GAME")
        try:
            data = self._zoo.to_dict()
            with open(SAVE_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            print(f"  ✅ Game saved to '{SAVE_FILE}'.")
        except Exception as e:
            print(f"  ❌ Save failed: {e}")
        _pause()

    # ------------------------------------------------------------------
    # [9] Load Game
    # ------------------------------------------------------------------

    def _menu_load_game(self) -> None:
        """Load a previously saved game state."""
        _header("LOAD GAME")
        if not os.path.exists(SAVE_FILE):
            print(f"  ❌ No save file found ('{SAVE_FILE}').")
            _pause()
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            # Restore Finance singleton state
            from finance import Finance
            Finance.reset()
            fin = Finance.get_instance()
            fin.from_dict(data.get("finance", {}))

            # Rebuild the zoo — minimal state restore
            self._zoo = Zoo(name=data.get("name", "OzZoo"))
            self._zoo.from_dict(data)
            self._game_loop = GameLoop(self._zoo)
            print(f"  ✅ Game loaded from '{SAVE_FILE}'.")
        except Exception as e:
            print(f"  ❌ Load failed: {e}")
        _pause()

    # ------------------------------------------------------------------
    # [0] Quit
    # ------------------------------------------------------------------

    def _quit(self) -> None:
        """Exit the simulation."""
        print(
            f"\n  Goodbye!  Final score: {self._zoo.score}\n"
            f"  OzZoo survived {self._zoo.day} days.  🦘\n"
        )
        self._running = False
