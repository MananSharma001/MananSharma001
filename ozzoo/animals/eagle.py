"""
eagle.py
--------
Eagle – concrete animal class.

Inheritance chain:  Eagle → Bird → Animal (ABC)
"""

from ozzoo.animals.bird import Bird


class Eagle(Bird):
    """
    A bald eagle: a powerful bird of prey.

    Inheritance chain:  Eagle → Bird → Animal

    Additional attributes
    ---------------------
    altitude_m : int – typical soaring altitude in metres
    """

    _ticket_price: float = 18.0

    def __init__(self, name: str, altitude_m: int = 3000, **kwargs) -> None:
        super().__init__(name=name, species="Haliaeetus leucocephalus",
                         wingspan_cm=210.0, can_fly=True, **kwargs)
        self.altitude_m = altitude_m

    def sound(self) -> str:
        return "SCREECH"

    def diet(self) -> str:
        return "carnivore"

    def dive(self) -> str:
        """High-speed dive to catch prey."""
        self.hunger -= 15
        self.happiness += 12
        return f"{self.name} dived at high speed! Hunger: {self.hunger}, Happiness: {self.happiness}"
