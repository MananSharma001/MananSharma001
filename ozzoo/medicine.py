"""
medicine.py
===========
Manages the zoo's medicine inventory.

Medicine types: ``"antibiotic"``, ``"vitamin"``, ``"vaccine"``, ``"painkiller"``
Each medicine type heals a different amount of health and costs differently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# ---------------------------------------------------------------------------
# Data class for a single medicine type
# ---------------------------------------------------------------------------

@dataclass
class MedicineItem:
    """
    Represents one category of medicine in the zoo's medical supplies.

    Attributes
    ----------
    medicine_type : str
        Identifier for this medicine (e.g. ``"antibiotic"``).
    quantity : int
        Number of doses in stock.
    cost_per_dose : float
        Price per dose in AUD.
    heal_amount : int
        Health points restored per dose.
    """

    medicine_type: str
    quantity: int = 0
    cost_per_dose: float = 15.0
    heal_amount: int = 20

    def __str__(self) -> str:
        return (
            f"MedicineItem({self.medicine_type}: qty={self.quantity}, "
            f"${self.cost_per_dose:.2f}/dose, heals={self.heal_amount}hp)"
        )

    def __repr__(self) -> str:
        return (
            f"MedicineItem(medicine_type={self.medicine_type!r}, "
            f"quantity={self.quantity}, cost_per_dose={self.cost_per_dose}, "
            f"heal_amount={self.heal_amount})"
        )


# ---------------------------------------------------------------------------
# Medicine inventory defaults
# ---------------------------------------------------------------------------

DEFAULT_MEDICINE: Dict[str, Dict] = {
    "antibiotic":  {"cost_per_dose": 20.0, "heal_amount": 30, "quantity": 10},
    "vitamin":     {"cost_per_dose": 8.0,  "heal_amount": 10, "quantity": 15},
    "vaccine":     {"cost_per_dose": 25.0, "heal_amount": 40, "quantity": 5},
    "painkiller":  {"cost_per_dose": 12.0, "heal_amount": 15, "quantity": 10},
}


class MedicineInventory:
    """
    Manages the zoo's medical supplies.

    Attributes
    ----------
    _inventory : Dict[str, MedicineItem]
        Maps medicine type name to its :class:`MedicineItem` record.
    """

    VALID_TYPES: frozenset[str] = frozenset(DEFAULT_MEDICINE.keys())

    def __init__(self) -> None:
        """Initialise medicine inventory with default stock."""
        self._inventory: Dict[str, MedicineItem] = {
            med_type: MedicineItem(
                medicine_type=med_type,
                quantity=info["quantity"],
                cost_per_dose=info["cost_per_dose"],
                heal_amount=info["heal_amount"],
            )
            for med_type, info in DEFAULT_MEDICINE.items()
        }

    # ------------------------------------------------------------------
    # Stock queries
    # ------------------------------------------------------------------

    def get_quantity(self, medicine_type: str) -> int:
        """
        Return current stock of *medicine_type*.

        Parameters
        ----------
        medicine_type : str
            Medicine category to query.

        Returns
        -------
        int
            Number of doses in stock.
        """
        self._validate_type(medicine_type)
        return self._inventory[medicine_type].quantity

    def get_heal_amount(self, medicine_type: str) -> int:
        """
        Return the health points restored per dose of *medicine_type*.

        Parameters
        ----------
        medicine_type : str
            Medicine category to query.

        Returns
        -------
        int
            Health points per dose.
        """
        self._validate_type(medicine_type)
        return self._inventory[medicine_type].heal_amount

    def get_cost(self, medicine_type: str) -> float:
        """
        Return the cost per dose of *medicine_type*.

        Parameters
        ----------
        medicine_type : str
            Medicine category to query.

        Returns
        -------
        float
            Cost in AUD per dose.
        """
        self._validate_type(medicine_type)
        return self._inventory[medicine_type].cost_per_dose

    # ------------------------------------------------------------------
    # Purchasing and administering
    # ------------------------------------------------------------------

    def purchase(self, medicine_type: str, doses: int) -> float:
        """
        Add *doses* to stock and return the total cost.

        Parameters
        ----------
        medicine_type : str
            Medicine category to purchase.
        doses : int
            Number of doses to buy.

        Returns
        -------
        float
            Total cost in AUD.

        Raises
        ------
        ValueError
            If *medicine_type* is invalid or *doses* <= 0.
        """
        self._validate_type(medicine_type)
        if doses <= 0:
            raise ValueError("Doses to purchase must be a positive integer.")
        item = self._inventory[medicine_type]
        item.quantity += doses
        return item.cost_per_dose * doses

    def administer(self, medicine_type: str, doses: int = 1) -> int:
        """
        Use *doses* from stock and return the total heal amount.

        Parameters
        ----------
        medicine_type : str
            Medicine category to administer.
        doses : int
            Number of doses to use.  Defaults to 1.

        Returns
        -------
        int
            Total health points that will be restored.

        Raises
        ------
        ValueError
            If there is not enough stock or *medicine_type* is invalid.
        """
        self._validate_type(medicine_type)
        item = self._inventory[medicine_type]
        if item.quantity < doses:
            raise ValueError(
                f"Insufficient '{medicine_type}' stock: "
                f"have {item.quantity}, need {doses}."
            )
        item.quantity -= doses
        return item.heal_amount * doses

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _validate_type(self, medicine_type: str) -> None:
        """Raise ValueError if *medicine_type* is not recognised."""
        if medicine_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unknown medicine type '{medicine_type}'.  "
                f"Valid types: {sorted(self.VALID_TYPES)}"
            )

    def report(self) -> str:
        """
        Return a formatted inventory report string.

        Returns
        -------
        str
            Multi-line report of all medicine stock.
        """
        lines = ["💊 Medicine Inventory:"]
        for item in self._inventory.values():
            lines.append(
                f"   {item.medicine_type:<12} qty={item.quantity:>4}  "
                f"(${item.cost_per_dose:.2f}/dose, +{item.heal_amount}hp)"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialise to a plain dict for JSON save/load."""
        return {
            k: {
                "quantity": v.quantity,
                "cost_per_dose": v.cost_per_dose,
                "heal_amount": v.heal_amount,
            }
            for k, v in self._inventory.items()
        }

    def from_dict(self, data: dict) -> None:
        """Restore inventory from a plain dict (from JSON)."""
        for med_type, values in data.items():
            if med_type in self._inventory:
                self._inventory[med_type].quantity = values.get("quantity", 0)
                self._inventory[med_type].cost_per_dose = values.get(
                    "cost_per_dose", DEFAULT_MEDICINE.get(med_type, {}).get("cost_per_dose", 15.0)
                )
                self._inventory[med_type].heal_amount = values.get(
                    "heal_amount", DEFAULT_MEDICINE.get(med_type, {}).get("heal_amount", 20)
                )

    def __str__(self) -> str:
        return self.report()

    def __repr__(self) -> str:
        total = sum(v.quantity for v in self._inventory.values())
        return f"MedicineInventory(total_doses={total})"
