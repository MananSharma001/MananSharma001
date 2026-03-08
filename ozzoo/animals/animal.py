"""
animals/animal.py
=================
Abstract base class for every animal in the OzZoo simulation.

All concrete animal classes *must* override the four abstract methods:
``make_sound()``, ``eat()``, ``sleep()``, and ``get_info()``.

Animal welfare attributes (health, hunger, happiness) are stored as
private attributes accessed via ``@property`` / ``@setter`` decorators.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class Animal(ABC):
    """
    Abstract base class representing an animal in the zoo.

    Parameters
    ----------
    name : str
        The animal's name.
    species : str
        The biological species label.
    age : int
        Age in years.
    habitat_type : str
        The enclosure habitat type this animal requires (e.g. "Savannah").
    required_food : str
        The food type this animal needs (e.g. "grass", "fish").
    """

    def __init__(
        self,
        name: str,
        species: str,
        age: int,
        habitat_type: str,
        required_food: str,
    ) -> None:
        """Initialise common animal attributes."""
        self._name: str = name
        self._species: str = species
        self._age: int = age
        self._habitat_type: str = habitat_type
        self._required_food: str = required_food
        self._is_alive: bool = True

        # Welfare stats — private; accessed via properties
        self.__health: int = 100
        self.__hunger: int = 0
        self.__happiness: int = 80

        # Track consecutive hungry days for health degradation
        self._hungry_days: int = 0

    # ------------------------------------------------------------------
    # Properties — encapsulated welfare stats
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """The animal's name."""
        return self._name

    @property
    def species(self) -> str:
        """The animal's species label."""
        return self._species

    @property
    def age(self) -> int:
        """The animal's age in years."""
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        """Set the animal's age (must be >= 0)."""
        if value < 0:
            raise ValueError("Age cannot be negative.")
        self._age = value

    @property
    def habitat_type(self) -> str:
        """The habitat type required by this animal."""
        return self._habitat_type

    @property
    def required_food(self) -> str:
        """The food type this animal eats."""
        return self._required_food

    @property
    def is_alive(self) -> bool:
        """Whether the animal is currently alive."""
        return self._is_alive

    @property
    def health(self) -> int:
        """Current health (0-100)."""
        return self.__health

    @health.setter
    def health(self, value: int) -> None:
        """Set health, clamped to [0, 100].  Marks animal as dead if 0."""
        self.__health = max(0, min(100, value))
        if self.__health == 0:
            self._is_alive = False

    @property
    def hunger(self) -> int:
        """Current hunger level (0-100; higher = more hungry)."""
        return self.__hunger

    @hunger.setter
    def hunger(self, value: int) -> None:
        """Set hunger, clamped to [0, 100]."""
        self.__hunger = max(0, min(100, value))

    @property
    def happiness(self) -> int:
        """Current happiness level (0-100)."""
        return self.__happiness

    @happiness.setter
    def happiness(self, value: int) -> None:
        """Set happiness, clamped to [0, 100]."""
        self.__happiness = max(0, min(100, value))

    # ------------------------------------------------------------------
    # Abstract methods — must be overridden by subclasses
    # ------------------------------------------------------------------

    @abstractmethod
    def make_sound(self) -> str:
        """
        Produce the animal's characteristic sound.

        Returns
        -------
        str
            A string description of the sound.
        """

    @abstractmethod
    def eat(self, amount: int = 1) -> str:
        """
        Feed the animal the given amount of its required food.

        Parameters
        ----------
        amount : int
            Number of food units consumed.

        Returns
        -------
        str
            A description of the eating action.
        """

    @abstractmethod
    def sleep(self) -> str:
        """
        Make the animal sleep to restore energy/happiness.

        Returns
        -------
        str
            A description of the sleeping action.
        """

    @abstractmethod
    def get_info(self) -> str:
        """
        Return a formatted summary of the animal's current state.

        Returns
        -------
        str
            Multi-line information string.
        """

    # ------------------------------------------------------------------
    # Common concrete methods
    # ------------------------------------------------------------------

    def is_healthy(self) -> bool:
        """
        Return True if the animal's health is above the critical threshold.

        Returns
        -------
        bool
            ``True`` when health >= 30.
        """
        return self.__health >= 30

    def is_happy(self) -> bool:
        """
        Return True if the animal's happiness is above 60.

        Returns
        -------
        bool
            ``True`` when happiness >= 60.
        """
        return self.__happiness >= 60

    def apply_medicine(self, amount: int = 20) -> str:
        """
        Administer medicine to restore the animal's health.

        Parameters
        ----------
        amount : int
            Health points to restore.  Defaults to 20.

        Returns
        -------
        str
            Result message.
        """
        old_health = self.__health
        self.health = self.__health + amount
        return (
            f"{self._name} received medicine.  "
            f"Health: {old_health} → {self.__health}"
        )

    def daily_tick(self) -> list[str]:
        """
        Simulate one day passing for this animal.

        Increases hunger and sleepiness; degrades health if the animal is
        very hungry or unhappy.  Returns a list of event messages.

        Returns
        -------
        list[str]
            Messages describing changes that occurred.
        """
        events: list[str] = []
        if not self._is_alive:
            return events

        # Hunger increases each day
        self.hunger = self.__hunger + 10

        # Happiness drifts down slightly each day
        self.happiness = self.__happiness - 3

        # If very hungry, count consecutive hungry days
        if self.__hunger > 80:
            self._hungry_days += 1
        else:
            self._hungry_days = 0

        # Health degradation from sustained hunger or unhappiness
        if self._hungry_days >= 2:
            self.health = self.__health - 10
            events.append(
                f"{self._name} is very hungry — health dropping! "
                f"(health={self.__health})"
            )

        if self.__happiness < 20:
            self.health = self.__health - 5
            events.append(
                f"{self._name} is very unhappy — health dropping! "
                f"(health={self.__health})"
            )

        if not self._is_alive:
            events.append(f"💀 {self._name} ({self._species}) has died.")

        return events

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        status = "alive" if self._is_alive else "deceased"
        return (
            f"{self._name} [{self._species}] — "
            f"age={self._age}, health={self.__health}, "
            f"hunger={self.__hunger}, happiness={self.__happiness} ({status})"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, species={self._species!r}, "
            f"age={self._age}, health={self.__health})"
        )
