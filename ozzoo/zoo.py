"""
zoo.py
------
Zoo – the top-level orchestrator class.

The Zoo owns a collection of Habitat objects and delegates financial
transactions to the Finance singleton.  It provides high-level operations
like admitting visitors, running a full simulation day, and producing
management reports.
"""

from __future__ import annotations

from ozzoo.habitat import Habitat
from ozzoo.finance import Finance
from ozzoo.animals.animal import Animal


class Zoo:
    """
    Top-level class that manages habitats, animals, and finances.

    This class does NOT inherit from any other custom class; it uses
    composition (has-a relationships) rather than inheritance:
      - Zoo  *has*  Finance  (singleton reference)
      - Zoo  *has*  list[Habitat]

    Attributes
    ----------
    name      : str           – zoo display name
    location  : str           – city / country
    _habitats : list[Habitat] – habitats managed by this zoo
    _finance  : Finance       – singleton financial ledger
    """

    def __init__(self, name: str, location: str = "Sydney, Australia") -> None:
        self.name = name
        self.location = location
        self._habitats: list[Habitat] = []
        self._finance: Finance = Finance()   # always returns the singleton

    # ------------------------------------------------------------------ #
    #  Habitat management                                                 #
    # ------------------------------------------------------------------ #

    def add_habitat(self, habitat: Habitat) -> str:
        self._habitats.append(habitat)
        return f"Habitat '{habitat.name}' added to {self.name}."

    def remove_habitat(self, habitat: Habitat) -> str:
        if habitat in self._habitats:
            self._habitats.remove(habitat)
            return f"Habitat '{habitat.name}' removed."
        return f"Habitat '{habitat.name}' not found."

    def get_habitat(self, name: str) -> Habitat | None:
        """Find a habitat by name."""
        for h in self._habitats:
            if h.name == name:
                return h
        return None

    # ------------------------------------------------------------------ #
    #  Animal placement                                                   #
    # ------------------------------------------------------------------ #

    def place_animal(self, animal: Animal, habitat_name: str) -> str:
        """Assign an animal to a named habitat."""
        habitat = self.get_habitat(habitat_name)
        if habitat is None:
            return f"Habitat '{habitat_name}' does not exist."
        return habitat.add_animal(animal)

    # ------------------------------------------------------------------ #
    #  Visitor admission                                                  #
    # ------------------------------------------------------------------ #

    def admit_visitors(self, count: int = 1) -> list[str]:
        """
        Admit visitors.  Each unique animal species in the zoo charges its
        own ticket price; visitors are charged per habitat they enter.
        """
        log: list[str] = []
        for habitat in self._habitats:
            for animal in habitat.animals:
                msg = self._finance.charge_admission(animal.ticket_price, count)
                log.append(f"  [{habitat.name}] {animal.name}: {msg}")
        return log

    # ------------------------------------------------------------------ #
    #  Simulation                                                         #
    # ------------------------------------------------------------------ #

    def simulate_day(self) -> list[str]:
        """Run one simulation day across all habitats."""
        log: list[str] = ["--- Day Simulation ---"]
        for habitat in self._habitats:
            log.append(f"[{habitat.name}]")
            log.extend(habitat.simulate_day())
        # Daily operating costs
        daily_ops = 500.0 * len(self._habitats)
        log.append(self._finance.record_expense("daily operations", daily_ops))
        return log

    # ------------------------------------------------------------------ #
    #  Reporting                                                          #
    # ------------------------------------------------------------------ #

    def full_report(self) -> str:
        """Print a complete zoo status report."""
        lines = [
            f"{'='*50}",
            f"  ZOO: {self.name}",
            f"  Location: {self.location}",
            f"  Habitats: {len(self._habitats)}",
            f"{'='*50}",
        ]
        for habitat in self._habitats:
            lines.append(habitat.report())
            lines.append("")
        lines.append(self._finance.report())
        return "\n".join(lines)

    def __str__(self) -> str:
        return f"Zoo('{self.name}', habitats={len(self._habitats)})"

    def __repr__(self) -> str:
        return f"Zoo(name={self.name!r}, location={self.location!r})"
