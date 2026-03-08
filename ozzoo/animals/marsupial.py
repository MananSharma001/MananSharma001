"""
animals/marsupial.py
====================
Defines the ``Marsupial`` class and concrete species ``Kangaroo`` and ``Koala``.

Hierarchy: Animal → Mammal → Marsupial
           Animal → Mammal → Marsupial → Kangaroo  (concrete)
           Animal → Mammal → Marsupial → Koala      (concrete)
"""

from __future__ import annotations

from abc import abstractmethod

from animals.mammal import Mammal


class Marsupial(Mammal):
    """
    Abstract class representing a marsupial (pouched mammal).

    Adds a pouch attribute and joey-carrying behaviour.  All Australian
    marsupials in OzZoo inherit from this class.

    Parameters
    ----------
    name : str
        The animal's name.
    species : str
        Biological species label.
    age : int
        Age in years.
    habitat_type : str
        Required habitat type.
    required_food : str
        Food type this marsupial eats.
    fur_colour : str
        Colour of the marsupial's fur.
    has_joey : bool
        Whether the marsupial is currently carrying a joey.
    """

    def __init__(
        self,
        name: str,
        species: str,
        age: int,
        habitat_type: str,
        required_food: str,
        fur_colour: str = "grey",
        has_joey: bool = False,
    ) -> None:
        """Initialise marsupial with joey attribute."""
        super().__init__(
            name=name,
            species=species,
            age=age,
            habitat_type=habitat_type,
            required_food=required_food,
            fur_colour=fur_colour,
        )
        self._has_pouch: bool = True
        self._has_joey: bool = has_joey

    @property
    def has_joey(self) -> bool:
        """Whether the marsupial is currently carrying a joey."""
        return self._has_joey

    @has_joey.setter
    def has_joey(self, value: bool) -> None:
        """Set whether the marsupial has a joey in its pouch."""
        self._has_joey = value

    @abstractmethod
    def make_sound(self) -> str:
        """Produce the marsupial's characteristic sound."""

    @abstractmethod
    def eat(self, amount: int = 1) -> str:
        """Feed the marsupial."""

    @abstractmethod
    def get_info(self) -> str:
        """Return formatted information about the marsupial."""

    def __str__(self) -> str:
        base = super().__str__()
        joey = " [carrying joey]" if self._has_joey else ""
        return f"{base}{joey}"


# ---------------------------------------------------------------------------
# Concrete Marsupial: Kangaroo
# ---------------------------------------------------------------------------

class Kangaroo(Marsupial):
    """
    Concrete implementation of a Red Kangaroo.

    Habitat : Savannah
    Food    : grass
    """

    SOUND: str = "thump-thump"
    SPECIES: str = "Red Kangaroo"
    HABITAT: str = "Savannah"
    FOOD: str = "grass"

    def __init__(self, name: str, age: int = 1, **kwargs) -> None:
        """
        Initialise a Kangaroo.

        Parameters
        ----------
        name : str
            The kangaroo's name.
        age : int
            Age in years.
        """
        super().__init__(
            name=name,
            species=self.SPECIES,
            age=age,
            habitat_type=self.HABITAT,
            required_food=self.FOOD,
            fur_colour="red-brown",
        )

    def make_sound(self) -> str:
        """
        Produce the kangaroo's thumping sound.

        Returns
        -------
        str
            Sound description.
        """
        return f"{self._name} thumps the ground: '{self.SOUND}!'"

    def eat(self, amount: int = 1) -> str:
        """
        Feed the kangaroo grass.

        Parameters
        ----------
        amount : int
            Number of grass units consumed.

        Returns
        -------
        str
            Eating description.
        """
        self.hunger = self.hunger - (amount * 20)
        self.happiness = self.happiness + 5
        return f"{self._name} happily grazes on {amount} portion(s) of grass. 🦘"

    def jump(self) -> str:
        """
        Make the kangaroo jump — a unique Kangaroo behaviour.

        Returns
        -------
        str
            Jump description.
        """
        self.happiness = self.happiness + 8
        return f"{self._name} leaps powerfully across the savannah! 🦘 (+8 happiness)"

    def box(self) -> str:
        """
        Make the kangaroo box — playful unique behaviour.

        Returns
        -------
        str
            Boxing description.
        """
        return f"{self._name} raises its front paws in a boxing stance! 🥊"

    def get_info(self) -> str:
        """
        Return a formatted summary of the kangaroo's state.

        Returns
        -------
        str
            Multi-line info string.
        """
        joey_str = "Yes 🍼" if self._has_joey else "No"
        return (
            f"🦘 Kangaroo: {self._name}\n"
            f"   Species   : {self._species}\n"
            f"   Age       : {self._age} yrs\n"
            f"   Habitat   : {self._habitat_type}\n"
            f"   Food      : {self._required_food}\n"
            f"   Fur       : {self._fur_colour}\n"
            f"   Has Joey  : {joey_str}\n"
            f"   Health    : {self.health}/100\n"
            f"   Hunger    : {self.hunger}/100\n"
            f"   Happiness : {self.happiness}/100\n"
            f"   Alive     : {self._is_alive}"
        )


# ---------------------------------------------------------------------------
# Concrete Marsupial: Koala
# ---------------------------------------------------------------------------

class Koala(Marsupial):
    """
    Concrete implementation of a Koala.

    Habitat : Forest
    Food    : fruit (eucalyptus leaves — modelled as fruit)
    """

    SOUND: str = "bellow"
    SPECIES: str = "Koala"
    HABITAT: str = "Forest"
    FOOD: str = "fruit"

    def __init__(self, name: str, age: int = 1, **kwargs) -> None:
        """
        Initialise a Koala.

        Parameters
        ----------
        name : str
            The koala's name.
        age : int
            Age in years.
        """
        super().__init__(
            name=name,
            species=self.SPECIES,
            age=age,
            habitat_type=self.HABITAT,
            required_food=self.FOOD,
            fur_colour="grey",
        )
        self._sleep_hours_per_day: int = 18  # Koalas sleep a LOT

    def make_sound(self) -> str:
        """
        Produce the koala's bellow.

        Returns
        -------
        str
            Sound description.
        """
        return f"{self._name} lets out a deep '{self.SOUND}!'"

    def eat(self, amount: int = 1) -> str:
        """
        Feed the koala eucalyptus leaves (modelled as fruit).

        Parameters
        ----------
        amount : int
            Number of food portions consumed.

        Returns
        -------
        str
            Eating description.
        """
        self.hunger = self.hunger - (amount * 15)
        self.happiness = self.happiness + 7
        return (
            f"{self._name} munches contentedly on {amount} portion(s) "
            f"of eucalyptus leaves. 🐨"
        )

    def sleep(self) -> str:
        """
        Koalas are champion sleepers — big happiness and health boost.

        Returns
        -------
        str
            Sleeping description.
        """
        boost = 20
        self.happiness = self.happiness + boost
        self.health = self.health + 5
        return (
            f"{self._name} sleeps for {self._sleep_hours_per_day} hours "
            f"in a gum tree. 😴 (+{boost} happiness)"
        )

    def climb(self) -> str:
        """
        Make the koala climb — unique Koala behaviour.

        Returns
        -------
        str
            Climbing description.
        """
        self.happiness = self.happiness + 5
        return f"{self._name} clings to a tall eucalyptus tree. 🐨🌿 (+5 happiness)"

    def get_info(self) -> str:
        """
        Return a formatted summary of the koala's state.

        Returns
        -------
        str
            Multi-line info string.
        """
        joey_str = "Yes 🍼" if self._has_joey else "No"
        return (
            f"🐨 Koala: {self._name}\n"
            f"   Species   : {self._species}\n"
            f"   Age       : {self._age} yrs\n"
            f"   Habitat   : {self._habitat_type}\n"
            f"   Food      : {self._required_food}\n"
            f"   Fur       : {self._fur_colour}\n"
            f"   Has Joey  : {joey_str}\n"
            f"   Sleep hrs : {self._sleep_hours_per_day}/day\n"
            f"   Health    : {self.health}/100\n"
            f"   Hunger    : {self.hunger}/100\n"
            f"   Happiness : {self.happiness}/100\n"
            f"   Alive     : {self._is_alive}"
        )
