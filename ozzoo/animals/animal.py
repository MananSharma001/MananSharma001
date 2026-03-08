"""
animal.py
---------
Abstract base class for every animal in OzZoo.

All private attributes use Python's double-underscore name-mangling
(__attr) so they cannot be accidentally accessed from outside the class.
Public read/write access is provided through @property and @<name>.setter
descriptors.
"""

from abc import ABC, abstractmethod


class Animal(ABC):
    """
    Abstract base class representing a generic zoo animal.

    Attributes (private, accessed via properties)
    ----------------------------------------------
    __name       : str   – display name of the individual animal
    __species    : str   – species label (set by subclasses)
    __health     : int   – health points, 0-100
    __hunger     : int   – hunger level, 0-100  (100 = very hungry)
    __happiness  : int   – happiness level, 0-100

    Class variable
    --------------
    _ticket_price : float – admission price charged per visit (shared by all animals)
    """

    _ticket_price: float = 10.0   # class-level default; subclasses may override

    def __init__(self, name: str, species: str,
                 health: int = 100, hunger: int = 0, happiness: int = 80) -> None:
        self.__name = name
        self.__species = species
        self.__health = health
        self.__hunger = hunger
        self.__happiness = happiness

    # ------------------------------------------------------------------ #
    #  Properties – encapsulated getters / setters                        #
    # ------------------------------------------------------------------ #

    @property
    def name(self) -> str:
        return self.__name

    @property
    def species(self) -> str:
        return self.__species

    @property
    def ticket_price(self) -> float:
        return self._ticket_price

    @property
    def health(self) -> int:
        return self.__health

    @health.setter
    def health(self, value: int) -> None:
        self.__health = max(0, min(100, value))

    @property
    def hunger(self) -> int:
        return self.__hunger

    @hunger.setter
    def hunger(self, value: int) -> None:
        self.__hunger = max(0, min(100, value))

    @property
    def happiness(self) -> int:
        return self.__happiness

    @happiness.setter
    def happiness(self, value: int) -> None:
        self.__happiness = max(0, min(100, value))

    # ------------------------------------------------------------------ #
    #  Abstract methods – every concrete animal MUST implement these      #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def sound(self) -> str:
        """Return the characteristic sound made by this animal."""

    @abstractmethod
    def diet(self) -> str:
        """Return what this animal eats (e.g. 'carnivore', 'herbivore')."""

    # ------------------------------------------------------------------ #
    #  Concrete behaviour shared by all animals                           #
    # ------------------------------------------------------------------ #

    def feed(self, amount: int = 20) -> str:
        """Reduce hunger and slightly boost happiness."""
        self.hunger -= amount
        self.happiness += 5
        return f"{self.name} has been fed. Hunger: {self.hunger}, Happiness: {self.happiness}"

    def play(self, duration_minutes: int = 15) -> str:
        """Increase happiness but also increase hunger."""
        self.happiness += duration_minutes // 5
        self.hunger += duration_minutes // 10
        return (f"{self.name} played for {duration_minutes} min. "
                f"Happiness: {self.happiness}, Hunger: {self.hunger}")

    def receive_treatment(self, points: int = 20) -> str:
        """Restore health points (vet visit)."""
        self.health += points
        return f"{self.name} received treatment. Health: {self.health}"

    def status(self) -> str:
        return (f"[{self.species}] {self.name} | "
                f"Health: {self.health} | Hunger: {self.hunger} | Happiness: {self.happiness}")

    def __str__(self) -> str:
        return self.status()

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(name={self.name!r}, "
                f"species={self.species!r})")
