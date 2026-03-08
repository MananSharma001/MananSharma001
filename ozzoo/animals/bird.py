"""
animals/bird.py
===============
Defines the ``Bird`` class and the concrete ``Eagle`` species.

Hierarchy: Animal → Bird
           Animal → Bird → Eagle  (concrete)
"""

from __future__ import annotations

from abc import abstractmethod

from animals.animal import Animal


class Bird(Animal):
    """
    Abstract class representing a bird.

    Adds wing span and flight capability attributes.

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
    can_fly : bool
        Whether the bird can fly.  Defaults to ``True``.
    """

    def __init__(
        self,
        name: str,
        species: str,
        age: int,
        habitat_type: str,
        required_food: str,
        wingspan_cm: float = 100.0,
        can_fly: bool = True,
    ) -> None:
        """Initialise bird with wingspan and flight capability."""
        super().__init__(
            name=name,
            species=species,
            age=age,
            habitat_type=habitat_type,
            required_food=required_food,
        )
        self._wingspan_cm: float = wingspan_cm
        self._can_fly: bool = can_fly

    @property
    def wingspan_cm(self) -> float:
        """Wingspan in centimetres."""
        return self._wingspan_cm

    @property
    def can_fly(self) -> bool:
        """Whether this bird can fly."""
        return self._can_fly

    def sleep(self) -> str:
        """
        Make the bird sleep on its perch.

        Returns
        -------
        str
            Description of the sleeping action.
        """
        boost = 8
        self.happiness = self.happiness + boost
        return f"{self._name} tucks its head under its wing and dozes. 😴 (+{boost} happiness)"

    @abstractmethod
    def make_sound(self) -> str:
        """Produce the bird's characteristic sound."""

    @abstractmethod
    def eat(self, amount: int = 1) -> str:
        """Feed the bird."""

    @abstractmethod
    def get_info(self) -> str:
        """Return formatted information about the bird."""

    def __str__(self) -> str:
        base = super().__str__()
        flight = "can fly" if self._can_fly else "flightless"
        return f"{base}, wingspan={self._wingspan_cm}cm ({flight})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, species={self._species!r}, "
            f"wingspan_cm={self._wingspan_cm})"
        )


# ---------------------------------------------------------------------------
# Concrete Bird: Eagle
# ---------------------------------------------------------------------------

class Eagle(Bird):
    """
    Concrete implementation of a Wedge-tailed Eagle.

    Habitat : Savannah
    Food    : meat
    """

    SOUND: str = "screech"
    SPECIES: str = "Wedge-tailed Eagle"
    HABITAT: str = "Savannah"
    FOOD: str = "meat"

    def __init__(self, name: str, age: int = 1, **kwargs) -> None:
        """
        Initialise an Eagle.

        Parameters
        ----------
        name : str
            The eagle's name.
        age : int
            Age in years.
        """
        super().__init__(
            name=name,
            species=self.SPECIES,
            age=age,
            habitat_type=self.HABITAT,
            required_food=self.FOOD,
            wingspan_cm=200.0,
            can_fly=True,
        )

    def make_sound(self) -> str:
        """
        Produce the eagle's screech.

        Returns
        -------
        str
            Sound description.
        """
        return f"{self._name} screeches loudly: '{self.SOUND}!'"

    def eat(self, amount: int = 1) -> str:
        """
        Feed the eagle meat.

        Parameters
        ----------
        amount : int
            Number of meat units consumed.

        Returns
        -------
        str
            Eating description.
        """
        self.hunger = self.hunger - (amount * 20)
        self.happiness = self.happiness + 5
        return f"{self._name} tears into {amount} portion(s) of meat ravenously. 🦅"

    def soar(self) -> str:
        """
        Make the eagle soar high above the enclosure.

        Returns
        -------
        str
            Soaring description.
        """
        self.happiness = self.happiness + 10
        return f"{self._name} soars majestically overhead. 🦅 (+10 happiness)"

    def get_info(self) -> str:
        """
        Return a formatted summary of the eagle's state.

        Returns
        -------
        str
            Multi-line info string.
        """
        return (
            f"🦅 Eagle: {self._name}\n"
            f"   Species   : {self._species}\n"
            f"   Age       : {self._age} yrs\n"
            f"   Habitat   : {self._habitat_type}\n"
            f"   Food      : {self._required_food}\n"
            f"   Wingspan  : {self._wingspan_cm} cm\n"
            f"   Health    : {self.health}/100\n"
            f"   Hunger    : {self.hunger}/100\n"
            f"   Happiness : {self.happiness}/100\n"
            f"   Alive     : {self._is_alive}"
        )
