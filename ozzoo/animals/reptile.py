"""
animals/reptile.py
==================
Defines the ``Reptile`` class and concrete species ``Crocodile`` and ``Snake``.

Hierarchy: Animal → Reptile
           Animal → Reptile → Crocodile  (concrete)
           Animal → Reptile → Snake      (concrete)
"""

from __future__ import annotations

from abc import abstractmethod

from animals.animal import Animal


class Reptile(Animal):
    """
    Abstract class representing a reptile.

    Adds cold-blooded and scale-colour attributes specific to reptiles.

    Parameters
    ----------
    name : str
        The reptile's name.
    species : str
        Biological species label.
    age : int
        Age in years.
    habitat_type : str
        Required habitat type.
    required_food : str
        Food type this reptile eats.
    scale_colour : str
        Colour of the reptile's scales.
    is_venomous : bool
        Whether the reptile is venomous.  Defaults to ``False``.
    """

    def __init__(
        self,
        name : str,
        species: str,
        age: int,
        habitat_type: str,
        required_food: str,
        scale_colour: str = "green",
        is_venomous: bool = False,
    ) -> None:
        """Initialise reptile with scale and venom attributes."""
        super().__init__(
            name=name,
            species=species,
            age=age,
            habitat_type=habitat_type,
            required_food=required_food,
        )
        self._scale_colour: str = scale_colour
        self._is_venomous: bool = is_venomous
        self._is_cold_blooded: bool = True

    @property
    def scale_colour(self) -> str:
        """Colour of the reptile's scales."""
        return self._scale_colour

    @property
    def is_venomous(self) -> bool:
        """Whether this reptile is venomous."""
        return self._is_venomous

    def sleep(self) -> str:
        """
        Make the reptile bask and rest.

        Returns
        -------
        str
            Description of the resting action.
        """
        boost = 12
        self.happiness = self.happiness + boost
        return f"{self._name} basks in the warm sun and rests. 🦎 (+{boost} happiness)"

    @abstractmethod
    def make_sound(self) -> str:
        """Produce the reptile's characteristic sound."""

    @abstractmethod
    def eat(self, amount: int = 1) -> str:
        """Feed the reptile."""

    @abstractmethod
    def get_info(self) -> str:
        """Return formatted information about the reptile."""

    def __str__(self) -> str:
        base = super().__str__()
        venomous = "venomous" if self._is_venomous else "non-venomous"
        return f"{base}, scales={self._scale_colour} ({venomous})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, species={self._species!r}, "
            f"venomous={self._is_venomous})"
        )


# ---------------------------------------------------------------------------
# Concrete Reptile: Crocodile
# ---------------------------------------------------------------------------

class Crocodile(Reptile):
    """
    Concrete implementation of a Saltwater Crocodile.

    Habitat : Wetlands
    Food    : meat
    """

    SOUND: str = "hiss"
    SPECIES: str = "Saltwater Crocodile"
    HABITAT: str = "Wetlands"
    FOOD: str = "meat"

    def __init__(self, name: str, age: int = 1, **kwargs) -> None:
        """
        Initialise a Crocodile.

        Parameters
        ----------
        name : str
            The crocodile's name.
        age : int
            Age in years.
        """
        super().__init__(
            name=name,
            species=self.SPECIES,
            age=age,
            habitat_type=self.HABITAT,
            required_food=self.FOOD,
            scale_colour="dark green",
            is_venomous=False,
        )

    def make_sound(self) -> str:
        """
        Produce the crocodile's hiss.

        Returns
        -------
        str
            Sound description.
        """
        return f"{self._name} lets out a terrifying '{self.SOUND}!'"

    def eat(self, amount: int = 1) -> str:
        """
        Feed the crocodile meat.

        Parameters
        ----------
        amount : int
            Number of meat units consumed.

        Returns
        -------
        str
            Eating description.
        """
        self.hunger = self.hunger - (amount * 25)
        self.happiness = self.happiness + 8
        return f"{self._name} snaps up {amount} portion(s) of meat with a mighty bite. 🐊"

    def snap(self) -> str:
        """
        Make the crocodile snap its jaws — a unique behaviour.

        Returns
        -------
        str
            Action description.
        """
        return f"{self._name} snaps its powerful jaws — SNAP! 🐊"

    def get_info(self) -> str:
        """
        Return a formatted summary of the crocodile's state.

        Returns
        -------
        str
            Multi-line info string.
        """
        return (
            f"🐊 Crocodile: {self._name}\n"
            f"   Species   : {self._species}\n"
            f"   Age       : {self._age} yrs\n"
            f"   Habitat   : {self._habitat_type}\n"
            f"   Food      : {self._required_food}\n"
            f"   Scales    : {self._scale_colour}\n"
            f"   Health    : {self.health}/100\n"
            f"   Hunger    : {self.hunger}/100\n"
            f"   Happiness : {self.happiness}/100\n"
            f"   Alive     : {self._is_alive}"
        )


# ---------------------------------------------------------------------------
# Concrete Reptile: Snake
# ---------------------------------------------------------------------------

class Snake(Reptile):
    """
    Concrete implementation of an Eastern Brown Snake.

    Habitat : Savannah
    Food    : meat (small prey / insects)
    """

    SOUND: str = "ssss"
    SPECIES: str = "Eastern Brown Snake"
    HABITAT: str = "Savannah"
    FOOD: str = "insects"

    def __init__(self, name: str, age: int = 1, **kwargs) -> None:
        """
        Initialise a Snake.

        Parameters
        ----------
        name : str
            The snake's name.
        age : int
            Age in years.
        """
        super().__init__(
            name=name,
            species=self.SPECIES,
            age=age,
            habitat_type=self.HABITAT,
            required_food=self.FOOD,
            scale_colour="brown",
            is_venomous=True,
        )

    def make_sound(self) -> str:
        """
        Produce the snake's hiss.

        Returns
        -------
        str
            Sound description.
        """
        return f"{self._name} hisses menacingly: '{self.SOUND}...'"

    def eat(self, amount: int = 1) -> str:
        """
        Feed the snake insects/small prey.

        Parameters
        ----------
        amount : int
            Number of food units consumed.

        Returns
        -------
        str
            Eating description.
        """
        self.hunger = self.hunger - (amount * 18)
        self.happiness = self.happiness + 5
        return f"{self._name} slowly swallows {amount} portion(s) of prey whole. 🐍"

    def slither(self) -> str:
        """
        Make the snake slither — a unique behaviour.

        Returns
        -------
        str
            Action description.
        """
        return f"{self._name} glides silently through the grass. 🐍"

    def get_info(self) -> str:
        """
        Return a formatted summary of the snake's state.

        Returns
        -------
        str
            Multi-line info string.
        """
        venomous_str = "⚠️ VENOMOUS" if self._is_venomous else "non-venomous"
        return (
            f"🐍 Snake: {self._name}\n"
            f"   Species   : {self._species}\n"
            f"   Age       : {self._age} yrs\n"
            f"   Habitat   : {self._habitat_type}\n"
            f"   Food      : {self._required_food}\n"
            f"   Scales    : {self._scale_colour} ({venomous_str})\n"
            f"   Health    : {self.health}/100\n"
            f"   Hunger    : {self.hunger}/100\n"
            f"   Happiness : {self.happiness}/100\n"
            f"   Alive     : {self._is_alive}"
        )
