"""
mammal.py
---------
Mammal – intermediate class that inherits from Animal.

Adds mammal-specific attributes:
  - fur_colour : str  – coat colour
  - is_warm_blooded : bool – always True for mammals (class constant)
"""

from ozzoo.animals.animal import Animal


class Mammal(Animal):
    """
    Intermediate subclass of Animal representing warm-blooded fur-bearing creatures.

    Inheritance chain:  Mammal → Animal (ABC)

    Extra attributes
    ----------------
    fur_colour     : str  – colour of the animal's coat / skin
    is_warm_blooded: bool – class constant, always True
    """

    is_warm_blooded: bool = True

    def __init__(self, name: str, species: str, fur_colour: str = "brown",
                 **kwargs) -> None:
        super().__init__(name, species, **kwargs)
        self.fur_colour = fur_colour

    def groom(self) -> str:
        """Grooming session: boosts happiness."""
        self.happiness += 10
        return f"{self.name} was groomed. Happiness: {self.happiness}"

    def diet(self) -> str:
        """Default diet label for mammals (overridden by concrete classes)."""
        return "omnivore"

    def sound(self) -> str:
        """Generic mammal sound (overridden by concrete classes)."""
        return "..."
