"""
lion.py
-------
Lion – concrete animal class.

Inheritance chain:  Lion → Mammal → Animal (ABC)
"""

from ozzoo.animals.mammal import Mammal


class Lion(Mammal):
    """
    A lion: the apex predator of the African savannah.

    Inheritance chain:  Lion → Mammal → Animal

    Additional attributes
    ---------------------
    mane_length : str – 'short', 'medium', or 'long' (males only)
    is_male     : bool
    """

    _ticket_price: float = 25.0   # lions attract a premium entrance fee

    def __init__(self, name: str, is_male: bool = True,
                 mane_length: str = "medium", **kwargs) -> None:
        super().__init__(name=name, species="Panthera leo",
                         fur_colour="golden", **kwargs)
        self.is_male = is_male
        self.mane_length = mane_length

    def sound(self) -> str:
        return "ROAR"

    def diet(self) -> str:
        return "carnivore"

    def hunt(self) -> str:
        """Simulate a hunt: drains energy but boosts happiness."""
        self.hunger += 20
        self.happiness += 10
        return f"{self.name} went on a hunt! Hunger: {self.hunger}, Happiness: {self.happiness}"
