"""
reptile.py
----------
Reptile – intermediate class that inherits from Animal.

Adds reptile-specific attributes:
  - scale_colour   : str  – dominant colour of the scales
  - is_venomous    : bool – whether the animal is venomous
  - is_warm_blooded: bool – class constant, always False (cold-blooded)
"""

from ozzoo.animals.animal import Animal


class Reptile(Animal):
    """
    Intermediate subclass of Animal representing cold-blooded, scaly vertebrates.

    Inheritance chain:  Reptile → Animal (ABC)

    Extra attributes
    ----------------
    scale_colour  : str  – colour of scales or skin
    is_venomous   : bool – True if the animal produces venom
    is_warm_blooded: bool – class constant, always False
    """

    is_warm_blooded: bool = False

    def __init__(self, name: str, species: str,
                 scale_colour: str = "green", is_venomous: bool = False,
                 **kwargs) -> None:
        super().__init__(name, species, **kwargs)
        self.scale_colour = scale_colour
        self.is_venomous = is_venomous

    def bask(self, minutes: int = 30) -> str:
        """Basking in the sun restores health for cold-blooded animals."""
        self.health += minutes // 10
        return f"{self.name} basked in the sun for {minutes} min. Health: {self.health}"

    def diet(self) -> str:
        """Default diet label for reptiles (overridden by concrete classes)."""
        return "carnivore"

    def sound(self) -> str:
        """Generic reptile sound (overridden by concrete classes)."""
        return "hiss"
