"""
bird.py
-------
Bird – intermediate class that inherits from Animal.

Adds bird-specific attributes:
  - wingspan_cm : float – wingspan in centimetres
  - can_fly     : bool  – whether the bird is capable of flight
"""

from ozzoo.animals.animal import Animal


class Bird(Animal):
    """
    Intermediate subclass of Animal representing feathered, egg-laying vertebrates.

    Inheritance chain:  Bird → Animal (ABC)

    Extra attributes
    ----------------
    wingspan_cm : float – wingspan measured in centimetres
    can_fly     : bool  – True if the bird is capable of sustained flight
    """

    is_warm_blooded: bool = True

    def __init__(self, name: str, species: str,
                 wingspan_cm: float = 50.0, can_fly: bool = True,
                 **kwargs) -> None:
        super().__init__(name, species, **kwargs)
        self.wingspan_cm = wingspan_cm
        self.can_fly = can_fly

    def fly(self) -> str:
        """Simulate a flight session; raises happiness if able to fly."""
        if self.can_fly:
            self.happiness += 15
            return f"{self.name} soared through the air! Happiness: {self.happiness}"
        return f"{self.name} cannot fly."

    def diet(self) -> str:
        """Default diet label for birds (overridden by concrete classes)."""
        return "omnivore"

    def sound(self) -> str:
        """Generic bird sound (overridden by concrete classes)."""
        return "tweet"
