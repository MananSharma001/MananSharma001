"""
gecko.py
--------
Gecko – concrete animal class.

Inheritance chain:  Gecko → Reptile → Animal (ABC)
"""

from ozzoo.animals.reptile import Reptile


class Gecko(Reptile):
    """
    A leopard gecko: a small, docile, and popular display reptile.

    Inheritance chain:  Gecko → Reptile → Animal

    Additional attributes
    ---------------------
    can_regrow_tail : bool – geckos can regenerate lost tails (always True)
    """

    _ticket_price: float = 8.0

    can_regrow_tail: bool = True  # class-level constant

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name=name, species="Eublepharis macularius",
                         scale_colour="yellow-spotted", is_venomous=False, **kwargs)

    def sound(self) -> str:
        return "chirp-chirp"

    def diet(self) -> str:
        return "insectivore"

    def climb_wall(self) -> str:
        """Geckos use adhesive toe pads to scale vertical surfaces."""
        self.happiness += 10
        return f"{self.name} climbed the enclosure wall! Happiness: {self.happiness}"
