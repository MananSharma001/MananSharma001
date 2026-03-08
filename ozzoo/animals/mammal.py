"""
animals/mammal.py
=================
Defines the ``Mammal`` class — a mid-level abstract class in the animal
hierarchy that adds mammal-specific attributes and a default ``sleep()``
implementation.

Hierarchy: Animal → Mammal
"""

from __future__ import annotations

from abc import abstractmethod

from animals.animal import Animal


class Mammal(Animal):
    """
    Abstract class representing a mammal.

    Adds fur colour and warm-blooded attributes common to all mammals.
    Subclasses must still implement :meth:`make_sound`, :meth:`eat`, and
    :meth:`get_info`.

    Parameters
    ----------
    name : str
        The animal's name.
    species : str
        Biological species label.
    age : int
        Age in years.
    habitat_type : str
        Required habitat type string.
    required_food : str
        Food type this mammal eats.
    fur_colour : str
        Colour of the mammal's fur/coat.
    """

    def __init__(
        self,
        name: str,
        species: str,
        age: int,
        habitat_type: str,
        required_food: str,
        fur_colour: str = "brown",
    ) -> None:
        """Initialise mammal with fur colour in addition to base attributes."""
        super().__init__(
            name=name,
            species=species,
            age=age,
            habitat_type=habitat_type,
            required_food=required_food,
        )
        self._fur_colour: str = fur_colour
        self._is_warm_blooded: bool = True

    @property
    def fur_colour(self) -> str:
        """The colour of the mammal's fur."""
        return self._fur_colour

    def sleep(self) -> str:
        """
        Make the mammal sleep, boosting its happiness.

        Returns
        -------
        str
            A description of the sleeping action.
        """
        boost = 10
        self.happiness = self.happiness + boost
        return f"{self._name} curls up and sleeps soundly. 😴 (+{boost} happiness)"

    @abstractmethod
    def make_sound(self) -> str:
        """Produce the mammal's characteristic sound."""

    @abstractmethod
    def eat(self, amount: int = 1) -> str:
        """Feed the mammal."""

    @abstractmethod
    def get_info(self) -> str:
        """Return formatted information about the mammal."""

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base}, fur={self._fur_colour}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, species={self._species!r}, "
            f"fur_colour={self._fur_colour!r})"
        )
