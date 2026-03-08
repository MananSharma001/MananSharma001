"""
animals/__init__.py
===================
Public API for the animals package.
"""

from .animal import Animal
from .mammal import Mammal
from .bird import Bird, Eagle
from .reptile import Reptile, Crocodile, Snake
from .marsupial import Marsupial, Kangaroo, Koala
from .flightless_bird import FlightlessBird, Penguin, Emu

__all__ = [
    "Animal",
    "Mammal",
    "Bird",
    "Eagle",
    "Reptile",
    "Crocodile",
    "Snake",
    "Marsupial",
    "Kangaroo",
    "Koala",
    "FlightlessBird",
    "Penguin",
    "Emu",
]


def feed_animal(animal: Animal, amount: int = 1) -> str:
    """
    Standalone polymorphic function to feed any animal.

    This demonstrates polymorphism — the correct ``eat()`` method is
    called regardless of the concrete animal subclass passed.

    Parameters
    ----------
    animal : Animal
        Any concrete Animal instance.
    amount : int
        Number of food units to give.

    Returns
    -------
    str
        The result message from the animal's ``eat()`` method.
    """
    return animal.eat(amount)
