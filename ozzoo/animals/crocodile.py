"""
crocodile.py
------------
Crocodile – concrete animal class.

Inheritance chain:  Crocodile → Reptile → Animal (ABC)
"""

from ozzoo.animals.reptile import Reptile


class Crocodile(Reptile):
    """
    A Nile crocodile: the apex reptilian predator of African rivers.

    Inheritance chain:  Crocodile → Reptile → Animal

    Additional attributes
    ---------------------
    length_m : float – body length in metres
    """

    _ticket_price: float = 15.0

    def __init__(self, name: str, length_m: float = 4.5, **kwargs) -> None:
        super().__init__(name=name, species="Crocodylus niloticus",
                         scale_colour="dark green", is_venomous=False, **kwargs)
        self.length_m = length_m

    def sound(self) -> str:
        return "HISS-SNAP"

    def diet(self) -> str:
        return "carnivore"

    def death_roll(self) -> str:
        """Signature hunting move: drains energy."""
        self.hunger += 15
        self.happiness += 20
        return f"{self.name} performed a death roll! Hunger: {self.hunger}, Happiness: {self.happiness}"
