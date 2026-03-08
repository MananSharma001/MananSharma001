"""
animals/flightless_bird.py
==========================
Defines the ``FlightlessBird`` class and concrete species ``Penguin`` and ``Emu``.

Hierarchy: Animal → Bird → FlightlessBird
           Animal → Bird → FlightlessBird → Penguin  (concrete)
           Animal → Bird → FlightlessBird → Emu      (concrete)
"""

from __future__ import annotations

from abc import abstractmethod

from animals.bird import Bird


class FlightlessBird(Bird):
    """
    Abstract class for birds that cannot fly.

    Sets ``can_fly=False`` and adds swimming / running speed attributes
    that are more relevant for flightless birds.

    Parameters
    ----------
    name : str
        The bird's name.
    species : str
        Biological species label.
    age : int
        Age in years.
    habitat_type : str
        Required habitat type.
    required_food : str
        Food type this bird eats.
    wingspan_cm : float
        Wingspan in centimetres.
    max_speed_kmh : float
        Maximum running/swimming speed in km/h.
    """

    def __init__(
        self,
        name: str,
        species: str,
        age: int,
        habitat_type: str,
        required_food: str,
        wingspan_cm: float = 50.0,
        max_speed_kmh: float = 20.0,
    ) -> None:
        """Initialise flightless bird with speed attribute."""
        super().__init__(
            name=name,
            species=species,
            age=age,
            habitat_type=habitat_type,
            required_food=required_food,
            wingspan_cm=wingspan_cm,
            can_fly=False,  # always False for flightless birds
        )
        self._max_speed_kmh: float = max_speed_kmh

    @property
    def max_speed_kmh(self) -> float:
        """Maximum movement speed in km/h."""
        return self._max_speed_kmh

    @abstractmethod
    def make_sound(self) -> str:
        """Produce the bird's characteristic sound."""

    @abstractmethod
    def eat(self, amount: int = 1) -> str:
        """Feed the bird."""

    @abstractmethod
    def get_info(self) -> str:
        """Return formatted information about this flightless bird."""

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base}, max_speed={self._max_speed_kmh} km/h"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, species={self._species!r}, "
            f"max_speed_kmh={self._max_speed_kmh})"
        )


# ---------------------------------------------------------------------------
# Concrete FlightlessBird: Penguin
# ---------------------------------------------------------------------------

class Penguin(FlightlessBird):
    """
    Concrete implementation of a Little Penguin.

    Habitat : Arctic
    Food    : fish
    """

    SOUND: str = "honk"
    SPECIES: str = "Little Penguin"
    HABITAT: str = "Arctic"
    FOOD: str = "fish"

    def __init__(self, name: str, age: int = 1, **kwargs) -> None:
        """
        Initialise a Penguin.

        Parameters
        ----------
        name : str
            The penguin's name.
        age : int
            Age in years.
        """
        super().__init__(
            name=name,
            species=self.SPECIES,
            age=age,
            habitat_type=self.HABITAT,
            required_food=self.FOOD,
            wingspan_cm=25.0,
            max_speed_kmh=25.0,  # swimming speed
        )
        self._can_swim: bool = True

    def make_sound(self) -> str:
        """
        Produce the penguin's honk.

        Returns
        -------
        str
            Sound description.
        """
        return f"{self._name} calls out: '{self.SOUND} {self.SOUND}!'"

    def eat(self, amount: int = 1) -> str:
        """
        Feed the penguin fish.

        Parameters
        ----------
        amount : int
            Number of fish units consumed.

        Returns
        -------
        str
            Eating description.
        """
        self.hunger = self.hunger - (amount * 20)
        self.happiness = self.happiness + 8
        return f"{self._name} gobbles up {amount} portion(s) of fish with delight. 🐧🐟"

    def swim(self) -> str:
        """
        Make the penguin swim — unique Penguin behaviour.

        Returns
        -------
        str
            Swimming description.
        """
        self.happiness = self.happiness + 12
        return (
            f"{self._name} dives gracefully into the icy water "
            f"at {self._max_speed_kmh} km/h! 🐧💨 (+12 happiness)"
        )

    def waddle(self) -> str:
        """
        Make the penguin waddle — another unique behaviour.

        Returns
        -------
        str
            Waddling description.
        """
        self.happiness = self.happiness + 3
        return f"{self._name} waddles adorably along the ice. 🐧 (+3 happiness)"

    def get_info(self) -> str:
        """
        Return a formatted summary of the penguin's state.

        Returns
        -------
        str
            Multi-line info string.
        """
        return (
            f"🐧 Penguin: {self._name}\n"
            f"   Species   : {self._species}\n"
            f"   Age       : {self._age} yrs\n"
            f"   Habitat   : {self._habitat_type}\n"
            f"   Food      : {self._required_food}\n"
            f"   Swim spd  : {self._max_speed_kmh} km/h\n"
            f"   Can swim  : {self._can_swim}\n"
            f"   Health    : {self.health}/100\n"
            f"   Hunger    : {self.hunger}/100\n"
            f"   Happiness : {self.happiness}/100\n"
            f"   Alive     : {self._is_alive}"
        )


# ---------------------------------------------------------------------------
# Concrete FlightlessBird: Emu
# ---------------------------------------------------------------------------

class Emu(FlightlessBird):
    """
    Concrete implementation of an Emu.

    Habitat : Savannah
    Food    : fruit
    """

    SOUND: str = "boom-boom"
    SPECIES: str = "Emu"
    HABITAT: str = "Savannah"
    FOOD: str = "fruit"

    def __init__(self, name: str, age: int = 1, **kwargs) -> None:
        """
        Initialise an Emu.

        Parameters
        ----------
        name : str
            The emu's name.
        age : int
            Age in years.
        """
        super().__init__(
            name=name,
            species=self.SPECIES,
            age=age,
            habitat_type=self.HABITAT,
            required_food=self.FOOD,
            wingspan_cm=20.0,
            max_speed_kmh=48.0,
        )

    def make_sound(self) -> str:
        """
        Produce the emu's booming drum sound.

        Returns
        -------
        str
            Sound description.
        """
        return f"{self._name} makes a deep booming sound: '{self.SOUND}!'"

    def eat(self, amount: int = 1) -> str:
        """
        Feed the emu fruit and vegetation.

        Parameters
        ----------
        amount : int
            Number of food portions consumed.

        Returns
        -------
        str
            Eating description.
        """
        self.hunger = self.hunger - (amount * 18)
        self.happiness = self.happiness + 6
        return f"{self._name} pecks hungrily at {amount} portion(s) of fruit. 🪶"

    def run(self) -> str:
        """
        Make the emu run — unique Emu behaviour.

        Returns
        -------
        str
            Running description.
        """
        self.happiness = self.happiness + 10
        return (
            f"{self._name} sprints across the savannah at "
            f"{self._max_speed_kmh} km/h! 🪶💨 (+10 happiness)"
        )

    def get_info(self) -> str:
        """
        Return a formatted summary of the emu's state.

        Returns
        -------
        str
            Multi-line info string.
        """
        return (
            f"🪶 Emu: {self._name}\n"
            f"   Species   : {self._species}\n"
            f"   Age       : {self._age} yrs\n"
            f"   Habitat   : {self._habitat_type}\n"
            f"   Food      : {self._required_food}\n"
            f"   Run speed : {self._max_speed_kmh} km/h\n"
            f"   Health    : {self.health}/100\n"
            f"   Hunger    : {self.hunger}/100\n"
            f"   Happiness : {self.happiness}/100\n"
            f"   Alive     : {self._is_alive}"
        )
