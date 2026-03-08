"""
food.py
=======
Manages the zoo's food inventory.

Food types available: ``"grass"``, ``"meat"``, ``"fish"``, ``"fruit"``, ``"insects"``

Each food type is tracked by quantity (units) and cost per unit in AUD.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from exceptions import InsufficientFoodError


# ---------------------------------------------------------------------------
# Data class for a single food type
# ---------------------------------------------------------------------------

@dataclass
class FoodItem:
    """
    Represents a single food category in the zoo's pantry.

    Attributes
    ----------
    food_type : str
        Name identifier for this food (e.g. ``"grass"``).
    quantity : int
        Current stock in units.
    cost_per_unit : float
        Price per unit in AUD when purchasing.
    """

    food_type: str
    quantity: int = 0
    cost_per_unit: float = 5.0

    def __str__(self) -> str:
        return (
            f"FoodItem({self.food_type}: qty={self.quantity}, "
            f"${self.cost_per_unit:.2f}/unit)"
        )

    def __repr__(self) -> str:
        return (
            f"FoodItem(food_type={self.food_type!r}, "
            f"quantity={self.quantity}, "
            f"cost_per_unit={self.cost_per_unit})"
        )


# ---------------------------------------------------------------------------
# Food inventory manager
# ---------------------------------------------------------------------------

# Default costs per food type (AUD per unit)
DEFAULT_COSTS: Dict[str, float] = {
    "grass": 2.0,
    "meat": 8.0,
    "fish": 6.0,
    "fruit": 3.0,
    "insects": 1.5,
}

# Default starting quantities
DEFAULT_QUANTITIES: Dict[str, int] = {
    "grass": 50,
    "meat": 30,
    "fish": 30,
    "fruit": 40,
    "insects": 25,
}


class FoodInventory:
    """
    Manages the zoo's food stock across all food types.

    Attributes
    ----------
    _inventory : Dict[str, FoodItem]
        Maps food type name to its :class:`FoodItem` record.
    """

    VALID_TYPES: frozenset[str] = frozenset(DEFAULT_COSTS.keys())

    def __init__(self) -> None:
        """Initialise food inventory with default stock levels."""
        self._inventory: Dict[str, FoodItem] = {
            food_type: FoodItem(
                food_type=food_type,
                quantity=DEFAULT_QUANTITIES[food_type],
                cost_per_unit=DEFAULT_COSTS[food_type],
            )
            for food_type in DEFAULT_COSTS
        }

    # ------------------------------------------------------------------
    # Stock queries
    # ------------------------------------------------------------------

    def get_quantity(self, food_type: str) -> int:
        """
        Return the current stock of *food_type*.

        Parameters
        ----------
        food_type : str
            The food category to query.

        Returns
        -------
        int
            Current stock in units.

        Raises
        ------
        ValueError
            If *food_type* is not a valid food category.
        """
        self._validate_type(food_type)
        return self._inventory[food_type].quantity

    def get_cost(self, food_type: str) -> float:
        """
        Return the cost per unit for *food_type*.

        Parameters
        ----------
        food_type : str
            The food category to query.

        Returns
        -------
        float
            Cost per unit in AUD.
        """
        self._validate_type(food_type)
        return self._inventory[food_type].cost_per_unit

    def total_stock(self) -> Dict[str, int]:
        """
        Return a dict mapping food type → current quantity.

        Returns
        -------
        Dict[str, int]
            Snapshot of all stock levels.
        """
        return {k: v.quantity for k, v in self._inventory.items()}

    # ------------------------------------------------------------------
    # Purchasing and consuming
    # ------------------------------------------------------------------

    def purchase(self, food_type: str, units: int) -> float:
        """
        Add *units* to the stock of *food_type* and return the total cost.

        Parameters
        ----------
        food_type : str
            Food category to purchase.
        units : int
            Number of units to buy.

        Returns
        -------
        float
            Total cost in AUD (units × cost_per_unit).

        Raises
        ------
        ValueError
            If *food_type* is invalid or *units* <= 0.
        """
        self._validate_type(food_type)
        if units <= 0:
            raise ValueError("Units to purchase must be a positive integer.")
        item = self._inventory[food_type]
        item.quantity += units
        return item.cost_per_unit * units

    def consume(self, food_type: str, units: int = 1) -> None:
        """
        Deduct *units* from the stock of *food_type*.

        Parameters
        ----------
        food_type : str
            Food category to consume.
        units : int
            Number of units to consume.

        Raises
        ------
        InsufficientFoodError
            If there is not enough stock to cover the requested consumption.
        ValueError
            If *food_type* is invalid.
        """
        self._validate_type(food_type)
        item = self._inventory[food_type]
        if item.quantity < units:
            raise InsufficientFoodError(
                f"Not enough '{food_type}' — have {item.quantity} unit(s), "
                f"need {units}."
            )
        item.quantity -= units

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _validate_type(self, food_type: str) -> None:
        """Raise ValueError if *food_type* is not a recognised category."""
        if food_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unknown food type '{food_type}'.  "
                f"Valid types: {sorted(self.VALID_TYPES)}"
            )

    def report(self) -> str:
        """
        Return a formatted inventory report string.

        Returns
        -------
        str
            Multi-line report of all food stock levels and costs.
        """
        lines = ["🍖 Food Inventory:"]
        for item in self._inventory.values():
            lines.append(
                f"   {item.food_type:<10} qty={item.quantity:>4}  "
                f"(${item.cost_per_unit:.2f}/unit)"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialise to a plain dict for JSON save/load."""
        return {
            k: {"quantity": v.quantity, "cost_per_unit": v.cost_per_unit}
            for k, v in self._inventory.items()
        }

    def from_dict(self, data: dict) -> None:
        """Restore inventory from a plain dict (from JSON)."""
        for food_type, values in data.items():
            if food_type in self._inventory:
                self._inventory[food_type].quantity = values.get("quantity", 0)
                self._inventory[food_type].cost_per_unit = values.get(
                    "cost_per_unit", DEFAULT_COSTS.get(food_type, 5.0)
                )

    def __str__(self) -> str:
        return self.report()

    def __repr__(self) -> str:
        total = sum(v.quantity for v in self._inventory.values())
        return f"FoodInventory(total_units={total})"
