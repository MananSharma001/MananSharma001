"""
visitor.py
==========
Defines the ``Visitor`` class representing zoo guests.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List


@dataclass
class Visitor:
    """
    Represents a zoo visitor (guest).

    Attributes
    ----------
    visitor_id : str
        Unique visitor identifier.
    name : str
        Visitor's display name.
    satisfaction : int
        Satisfaction level (0-100).  Starts at 70.
    ticket_price_paid : float
        Ticket price this visitor paid in AUD.
    favourite_animal : str
        Species name of the visitor's favourite animal.
    """

    visitor_id: str
    name: str
    satisfaction: int = 70
    ticket_price_paid: float = 25.0
    favourite_animal: str = "Kangaroo"
    _visited_enclosures: List[str] = field(default_factory=list, repr=False)

    def visit_enclosure(self, enclosure_name: str) -> str:
        """
        Record a visit to an enclosure and adjust satisfaction.

        Parameters
        ----------
        enclosure_name : str
            Name of the enclosure visited.

        Returns
        -------
        str
            Reaction message.
        """
        self._visited_enclosures.append(enclosure_name)
        boost = random.randint(5, 15)
        self.satisfaction = min(100, self.satisfaction + boost)
        return (
            f"{self.name} visits '{enclosure_name}' "
            f"and is delighted! (+{boost} satisfaction)"
        )

    def get_satisfaction_label(self) -> str:
        """
        Return a human-readable satisfaction label.

        Returns
        -------
        str
            One of ``"Ecstatic"``, ``"Happy"``, ``"Content"``,
            ``"Bored"``, ``"Unhappy"``.
        """
        if self.satisfaction >= 90:
            return "Ecstatic 🤩"
        if self.satisfaction >= 70:
            return "Happy 😊"
        if self.satisfaction >= 50:
            return "Content 😐"
        if self.satisfaction >= 30:
            return "Bored 😑"
        return "Unhappy 😞"

    def leave_donation(self, amount: float) -> str:
        """
        Make the visitor leave a donation.

        Parameters
        ----------
        amount : float
            Donation amount in AUD.

        Returns
        -------
        str
            Confirmation message.
        """
        return f"{self.name} donated ${amount:.2f} AUD to OzZoo! 💝"

    def __str__(self) -> str:
        return (
            f"Visitor({self.name}, satisfaction={self.satisfaction} "
            f"[{self.get_satisfaction_label()}], "
            f"ticket=${self.ticket_price_paid:.2f})"
        )

    def __repr__(self) -> str:
        return (
            f"Visitor(visitor_id={self.visitor_id!r}, name={self.name!r}, "
            f"satisfaction={self.satisfaction})"
        )


def generate_visitors(count: int, ticket_price: float) -> List[Visitor]:
    """
    Generate a list of *count* random visitor objects.

    Parameters
    ----------
    count : int
        Number of visitors to generate.
    ticket_price : float
        Ticket price in AUD.

    Returns
    -------
    List[Visitor]
        Randomly generated visitor list.
    """
    names = [
        "Alice", "Bob", "Charlie", "Diana", "Ethan",
        "Fiona", "George", "Hannah", "Ivan", "Julia",
        "Kevin", "Laura", "Mike", "Nancy", "Oscar",
        "Petra", "Quinn", "Rachel", "Sam", "Tina",
    ]
    animals = ["Kangaroo", "Koala", "Penguin", "Emu", "Crocodile", "Eagle", "Snake"]
    visitors: List[Visitor] = []
    for i in range(count):
        name = random.choice(names) + f"_{i + 1}"
        visitors.append(
            Visitor(
                visitor_id=f"VIS-{i + 1:04d}",
                name=name,
                satisfaction=random.randint(60, 90),
                ticket_price_paid=ticket_price,
                favourite_animal=random.choice(animals),
            )
        )
    return visitors
