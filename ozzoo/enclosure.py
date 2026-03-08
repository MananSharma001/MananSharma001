"""
enclosure.py
============
Defines the ``Enclosure`` class — a physical housing unit within a habitat.

``Enclosure`` implements :class:`~interfaces.icleanable.ICleanable` so it
can be cleaned by zoo keepers.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, List, Optional

from interfaces.icleanable import ICleanable
from exceptions import (
    HabitatCapacityExceededError,
    IncompatibleSpeciesError,
)

if TYPE_CHECKING:
    from animals.animal import Animal


class Enclosure(ICleanable):
    """
    Represents a single animal enclosure within the zoo.

    Each enclosure has a fixed maximum capacity, a required habitat type
    (e.g. ``"Savannah"``), and a cleanliness level that degrades over time.

    Parameters
    ----------
    enclosure_id : str
        Unique identifier for the enclosure (e.g. ``"ENC-001"``).
    name : str
        Human-readable name.
    habitat_type : str
        The type of environment the enclosure simulates.
    max_capacity : int
        Maximum number of animals allowed.
    area_m2 : float
        Floor area in square metres.
    """

    CLEANLINESS_DECAY: int = 10  # points lost per day
    UPGRADE_COST: float = 500.0  # AUD per upgrade

    def __init__(
        self,
        enclosure_id: str,
        name: str,
        habitat_type: str,
        max_capacity: int = 5,
        area_m2: float = 200.0,
    ) -> None:
        """Initialise the enclosure with no animals and full cleanliness."""
        self._enclosure_id: str = enclosure_id
        self._name: str = name
        self._habitat_type: str = habitat_type
        self._max_capacity: int = max_capacity
        self._area_m2: float = area_m2
        self.__cleanliness: int = 100  # private; 0-100
        self._animals: List["Animal"] = []
        self._upgrade_level: int = 1

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def enclosure_id(self) -> str:
        """Unique enclosure identifier."""
        return self._enclosure_id

    @property
    def name(self) -> str:
        """Human-readable name of the enclosure."""
        return self._name

    @property
    def habitat_type(self) -> str:
        """The habitat type this enclosure simulates."""
        return self._habitat_type

    @property
    def max_capacity(self) -> int:
        """Maximum number of animals this enclosure can hold."""
        return self._max_capacity

    @property
    def area_m2(self) -> float:
        """Floor area in square metres."""
        return self._area_m2

    @property
    def cleanliness(self) -> int:
        """Current cleanliness level (0-100)."""
        return self.__cleanliness

    @property
    def animals(self) -> List["Animal"]:
        """List of animals currently in this enclosure."""
        return list(self._animals)

    @property
    def animal_count(self) -> int:
        """Number of animals currently in the enclosure."""
        return len(self._animals)

    @property
    def upgrade_level(self) -> int:
        """Current upgrade level of the enclosure."""
        return self._upgrade_level

    # ------------------------------------------------------------------
    # Animal management
    # ------------------------------------------------------------------

    def add_animal(self, animal: "Animal") -> str:
        """
        Place an animal into this enclosure.

        Parameters
        ----------
        animal : Animal
            The animal to add.

        Returns
        -------
        str
            Confirmation message.

        Raises
        ------
        HabitatCapacityExceededError
            If the enclosure is at full capacity.
        IncompatibleSpeciesError
            If the animal's habitat type does not match this enclosure.
        """
        if len(self._animals) >= self._max_capacity:
            raise HabitatCapacityExceededError(
                f"Enclosure '{self._name}' is full "
                f"({self._max_capacity}/{self._max_capacity})."
            )
        if animal.habitat_type != self._habitat_type:
            raise IncompatibleSpeciesError(
                f"{animal.name} requires '{animal.habitat_type}' habitat, "
                f"but '{self._name}' is a '{self._habitat_type}' enclosure."
            )
        self._animals.append(animal)
        # Dirty the enclosure slightly
        self.__cleanliness = max(0, self.__cleanliness - 5)
        return (
            f"{animal.name} has been placed in {self._name}. "
            f"({len(self._animals)}/{self._max_capacity} animals)"
        )

    def remove_animal(self, animal: "Animal") -> Optional[str]:
        """
        Remove an animal from this enclosure.

        Parameters
        ----------
        animal : Animal
            The animal to remove.

        Returns
        -------
        Optional[str]
            Confirmation message, or ``None`` if the animal was not found.
        """
        if animal in self._animals:
            self._animals.remove(animal)
            return f"{animal.name} has been removed from {self._name}."
        return None

    # ------------------------------------------------------------------
    # ICleanable implementation
    # ------------------------------------------------------------------

    def clean(self) -> str:
        """
        Clean the enclosure, restoring cleanliness to 100.

        Returns
        -------
        str
            A message describing the cleaning action.
        """
        self.__cleanliness = 100
        return f"🧹 {self._name} has been thoroughly cleaned! (cleanliness=100)"

    # ------------------------------------------------------------------
    # Daily simulation
    # ------------------------------------------------------------------

    def daily_tick(self) -> list[str]:
        """
        Simulate one day passing for this enclosure.

        Cleanliness degrades; very dirty enclosures reduce animal happiness.

        Returns
        -------
        list[str]
            Event messages for the day.
        """
        events: list[str] = []
        self.__cleanliness = max(0, self.__cleanliness - self.CLEANLINESS_DECAY)

        if self.__cleanliness < 30:
            for animal in self._animals:
                if animal.is_alive:
                    animal.happiness = animal.happiness - 5
            events.append(
                f"⚠️  {self._name} is very dirty (cleanliness={self.__cleanliness}). "
                f"Animals are unhappy."
            )
        return events

    # ------------------------------------------------------------------
    # Upgrade
    # ------------------------------------------------------------------

    def upgrade(self) -> str:
        """
        Upgrade the enclosure, increasing its capacity by 2.

        Returns
        -------
        str
            A message describing the upgrade.
        """
        self._upgrade_level += 1
        self._max_capacity += 2
        self._area_m2 += 50.0
        return (
            f"🔧 {self._name} upgraded to level {self._upgrade_level}! "
            f"Capacity: {self._max_capacity}, Area: {self._area_m2} m²"
        )

    # ------------------------------------------------------------------
    # Breeding check
    # ------------------------------------------------------------------

    def check_breeding(self) -> Optional[str]:
        """
        Check if any two compatible animals in this enclosure should breed.

        Breeding condition: same species, both health > 70, happiness > 60,
        10 % daily chance.

        Returns
        -------
        Optional[str]
            A new-animal-born message if a birth occurred, else ``None``.
        """
        alive = [a for a in self._animals if a.is_alive]
        species_groups: dict[str, list] = {}
        for a in alive:
            species_groups.setdefault(a.species, []).append(a)

        for species, group in species_groups.items():
            if len(group) >= 2:
                candidates = [
                    a for a in group if a.health > 70 and a.happiness > 60
                ]
                if len(candidates) >= 2 and random.random() < 0.10:
                    parent = candidates[0]
                    # Create a new animal of the same class
                    try:
                        baby = parent.__class__(name=f"Baby_{species.split()[0]}", age=0)
                        if len(self._animals) < self._max_capacity:
                            self._animals.append(baby)
                            return (
                                f"🍼 A new {species} was born in {self._name}! "
                                f"Welcome, {baby.name}!"
                            )
                    except Exception:
                        pass
        return None

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def get_summary(self) -> str:
        """
        Return a formatted summary of this enclosure.

        Returns
        -------
        str
            Multi-line summary string.
        """
        animal_list = (
            "\n".join(f"      • {a}" for a in self._animals)
            if self._animals
            else "      (empty)"
        )
        return (
            f"🏠 Enclosure: {self._name} (ID: {self._enclosure_id})\n"
            f"   Habitat    : {self._habitat_type}\n"
            f"   Capacity   : {len(self._animals)}/{self._max_capacity}\n"
            f"   Area       : {self._area_m2} m²\n"
            f"   Cleanliness: {self.__cleanliness}/100\n"
            f"   Upgrade Lvl: {self._upgrade_level}\n"
            f"   Animals:\n{animal_list}"
        )

    def __str__(self) -> str:
        return (
            f"Enclosure({self._name!r}, {self._habitat_type}, "
            f"{len(self._animals)}/{self._max_capacity} animals, "
            f"cleanliness={self.__cleanliness})"
        )

    def __repr__(self) -> str:
        return (
            f"Enclosure(id={self._enclosure_id!r}, name={self._name!r}, "
            f"habitat_type={self._habitat_type!r}, "
            f"max_capacity={self._max_capacity})"
        )
