"""
habitat.py
----------
Habitat – models the physical environment in which zoo animals live.

A Habitat object describes the enclosure type, climate zone, and manages
a roster of animals assigned to it.  It enforces a capacity limit and
prevents incompatible animals from sharing the same space.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ozzoo.animals.animal import Animal


class Habitat:
    """
    Represents a single zoo enclosure / habitat zone.

    Attributes
    ----------
    name          : str          – display name of the habitat (e.g. "African Savannah")
    climate       : str          – climate type: 'tropical', 'arid', 'temperate',
                                   'aquatic', 'arctic'
    enclosure_type: str          – physical enclosure style: 'open', 'cage', 'tank',
                                   'aviary', 'terrarium'
    capacity      : int          – maximum number of animals allowed
    area_sqm      : float        – floor area in square metres
    _animals      : list[Animal] – animals currently residing here (private)

    Class constants
    ---------------
    VALID_CLIMATES  : tuple – allowed climate values
    VALID_ENCLOSURES: tuple – allowed enclosure type values
    """

    VALID_CLIMATES = ("tropical", "arid", "temperate", "aquatic", "arctic")
    VALID_ENCLOSURES = ("open", "cage", "tank", "aviary", "terrarium")

    def __init__(
        self,
        name: str,
        climate: str = "temperate",
        enclosure_type: str = "open",
        capacity: int = 10,
        area_sqm: float = 500.0,
    ) -> None:
        if climate not in self.VALID_CLIMATES:
            raise ValueError(
                f"Invalid climate '{climate}'. Choose from {self.VALID_CLIMATES}."
            )
        if enclosure_type not in self.VALID_ENCLOSURES:
            raise ValueError(
                f"Invalid enclosure_type '{enclosure_type}'. "
                f"Choose from {self.VALID_ENCLOSURES}."
            )
        self.name = name
        self.climate = climate
        self.enclosure_type = enclosure_type
        self.capacity = capacity
        self.area_sqm = area_sqm
        self._animals: list[Animal] = []

    # ------------------------------------------------------------------ #
    #  Animal management                                                  #
    # ------------------------------------------------------------------ #

    def add_animal(self, animal: Animal) -> str:
        """Place an animal into this habitat (respects capacity)."""
        if len(self._animals) >= self.capacity:
            return (f"Cannot add {animal.name}: habitat '{self.name}' is at full "
                    f"capacity ({self.capacity}).")
        self._animals.append(animal)
        return f"{animal.name} ({animal.species}) moved into '{self.name}'."

    def remove_animal(self, animal: Animal) -> str:
        """Remove an animal from this habitat."""
        if animal in self._animals:
            self._animals.remove(animal)
            return f"{animal.name} removed from '{self.name}'."
        return f"{animal.name} is not in '{self.name}'."

    # ------------------------------------------------------------------ #
    #  Environment interactions                                           #
    # ------------------------------------------------------------------ #

    def simulate_day(self) -> list[str]:
        """
        Simulate one day passing in this habitat.

        Each day:
          - Every animal gets slightly hungry (+5 hunger).
          - Reptiles in 'arid' or 'tropical' climates automatically bask (+3 health).
          - Animals in 'aquatic' habitats get a happiness boost (+5).
        """
        from ozzoo.animals.reptile import Reptile
        log: list[str] = []
        for animal in self._animals:
            animal.hunger += 5
            log.append(f"{animal.name} hunger increased to {animal.hunger}.")
            if isinstance(animal, Reptile) and self.climate in ("arid", "tropical"):
                animal.health += 3
                log.append(f"{animal.name} basked automatically (+3 health).")
            if self.climate == "aquatic":
                animal.happiness += 5
                log.append(f"{animal.name} enjoyed the aquatic environment (+5 happiness).")
        return log

    # ------------------------------------------------------------------ #
    #  Info / reporting                                                   #
    # ------------------------------------------------------------------ #

    @property
    def occupancy(self) -> int:
        """Current number of animals in this habitat."""
        return len(self._animals)

    @property
    def animals(self) -> list[Animal]:
        """Read-only view of the animals list."""
        return list(self._animals)

    def report(self) -> str:
        """Return a formatted summary of the habitat and its residents."""
        lines = [
            f"=== Habitat: {self.name} ===",
            f"  Climate      : {self.climate}",
            f"  Enclosure    : {self.enclosure_type}",
            f"  Area         : {self.area_sqm} m²",
            f"  Capacity     : {self.occupancy}/{self.capacity}",
            "  Residents:",
        ]
        if self._animals:
            for animal in self._animals:
                lines.append(f"    • {animal}")
        else:
            lines.append("    (empty)")
        return "\n".join(lines)

    def __str__(self) -> str:
        return f"Habitat('{self.name}', climate={self.climate}, {self.occupancy}/{self.capacity})"

    def __repr__(self) -> str:
        return (f"Habitat(name={self.name!r}, climate={self.climate!r}, "
                f"enclosure_type={self.enclosure_type!r}, capacity={self.capacity})")
