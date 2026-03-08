"""
elephant.py
-----------
Elephant – concrete animal class.

Inheritance chain:  Elephant → Mammal → Animal (ABC)
"""

from ozzoo.animals.mammal import Mammal


class Elephant(Mammal):
    """
    An African elephant: the largest land animal on Earth.

    Inheritance chain:  Elephant → Mammal → Animal

    Additional attributes
    ---------------------
    tusk_length_cm : float – average tusk length in centimetres
    """

    _ticket_price: float = 20.0

    def __init__(self, name: str, tusk_length_cm: float = 150.0, **kwargs) -> None:
        super().__init__(name=name, species="Loxodonta africana",
                         fur_colour="grey", **kwargs)
        self.tusk_length_cm = tusk_length_cm

    def sound(self) -> str:
        return "TRUMPET"

    def diet(self) -> str:
        return "herbivore"

    def spray_water(self) -> str:
        """Elephants cool themselves by spraying water."""
        self.health += 5
        self.happiness += 8
        return f"{self.name} sprayed water. Health: {self.health}, Happiness: {self.happiness}"
