"""
finance.py
==========
Implements the **Singleton** Finance manager for the OzZoo simulation.

Only *one* ``Finance`` instance exists per Python session.  All modules
that need to query or modify the zoo's balance should call
``Finance.get_instance()`` rather than constructing a new object.

Income sources  : ticket sales, donations
Expense sources : food, medicine, construction, upgrades, fines
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from exceptions import InsufficientFundsError


class Finance:
    """
    Singleton financial manager for the zoo.

    Tracks all income and expenses with timestamped ledger entries.

    Attributes
    ----------
    __balance : float
        Current available funds in AUD (private).
    _income_ledger : List[Tuple]
        Ordered record of all income transactions.
    _expense_ledger : List[Tuple]
        Ordered record of all expense transactions.
    """

    _instance: Optional["Finance"] = None
    STARTING_BALANCE: float = 10_000.0

    def __new__(cls) -> "Finance":
        """Enforce the singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self) -> None:
        """Initialise the Finance singleton (only runs once)."""
        if self._initialised:
            return
        self.__balance: float = self.STARTING_BALANCE
        self._income_ledger: List[Tuple[str, float, str, str]] = []
        # (timestamp, amount, source, description)
        self._expense_ledger: List[Tuple[str, float, str, str]] = []
        self._total_income: float = 0.0
        self._total_expenses: float = 0.0
        self._initialised = True

    # ------------------------------------------------------------------
    # Singleton accessor
    # ------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "Finance":
        """
        Return the single Finance instance, creating it if necessary.

        Returns
        -------
        Finance
            The global Finance singleton.
        """
        if cls._instance is None:
            cls()
        return cls._instance  # type: ignore[return-value]

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton (useful for testing).

        This destroys the existing instance so the next call to
        ``get_instance()`` creates a fresh Finance object.
        """
        cls._instance = None

    # ------------------------------------------------------------------
    # Balance queries
    # ------------------------------------------------------------------

    def get_balance(self) -> float:
        """
        Return the current zoo balance in AUD.

        Returns
        -------
        float
            Current balance.
        """
        return self.__balance

    # ------------------------------------------------------------------
    # Income and expenses
    # ------------------------------------------------------------------

    def add_income(self, amount: float, source: str, description: str = "") -> None:
        """
        Credit the zoo's account with *amount* from *source*.

        Parameters
        ----------
        amount : float
            Positive monetary amount in AUD.
        source : str
            Category label (e.g. ``"ticket_sales"``, ``"donation"``).
        description : str
            Optional free-text note.

        Raises
        ------
        ValueError
            If *amount* is not positive.
        """
        if amount <= 0:
            raise ValueError("Income amount must be positive.")
        self.__balance += amount
        self._total_income += amount
        self._income_ledger.append(
            (datetime.now().isoformat(), amount, source, description)
        )

    def deduct_expense(
        self, amount: float, category: str, description: str = ""
    ) -> None:
        """
        Debit *amount* from the zoo's account for *category*.

        Parameters
        ----------
        amount : float
            Positive monetary amount in AUD.
        category : str
            Expense category (e.g. ``"food"``, ``"medicine"``, ``"construction"``).
        description : str
            Optional free-text note.

        Raises
        ------
        InsufficientFundsError
            If the zoo does not have enough funds.
        ValueError
            If *amount* is not positive.
        """
        if amount <= 0:
            raise ValueError("Expense amount must be positive.")
        if amount > self.__balance:
            raise InsufficientFundsError(
                f"Cannot spend ${amount:,.2f} AUD — "
                f"only ${self.__balance:,.2f} AUD available."
            )
        self.__balance -= amount
        self._total_expenses += amount
        self._expense_ledger.append(
            (datetime.now().isoformat(), amount, category, description)
        )

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_report(self) -> str:
        """
        Return a formatted financial summary report.

        Returns
        -------
        str
            Multi-line financial report.
        """
        recent_income = self._income_ledger[-5:] if self._income_ledger else []
        recent_expenses = self._expense_ledger[-5:] if self._expense_ledger else []

        income_lines = "\n".join(
            f"   [{ts[:10]}] +${amt:>10,.2f}  {src:<18} {desc}"
            for ts, amt, src, desc in recent_income
        ) or "   (none)"

        expense_lines = "\n".join(
            f"   [{ts[:10]}] -${amt:>10,.2f}  {cat:<18} {desc}"
            for ts, amt, cat, desc in recent_expenses
        ) or "   (none)"

        return (
            "=" * 50 + "\n"
            + "        💰 FINANCIAL REPORT (AUD)\n"
            + "=" * 50 + "\n"
            + f"  Current Balance : ${self.__balance:>12,.2f}\n"
            + f"  Total Income    : ${self._total_income:>12,.2f}\n"
            + f"  Total Expenses  : ${self._total_expenses:>12,.2f}\n"
            + "─" * 50 + "\n"
            + "  Recent Income:\n"
            + f"{income_lines}\n"
            + "  Recent Expenses:\n"
            + f"{expense_lines}\n"
            + "=" * 50
        )

    def get_recent_ledger(self, n: int = 20) -> tuple[list, list]:
        """
        Return the *n* most recent income and expense ledger entries.

        Returns
        -------
        tuple[list, list]
            ``(income_entries, expense_entries)`` where each entry is a
            ``(timestamp, amount, category, description)`` tuple.
        """
        return (list(self._income_ledger[-n:]),
                list(self._expense_ledger[-n:]))

    def get_income_by_source(self) -> Dict[str, float]:
        """
        Return a dict aggregating total income per source.

        Returns
        -------
        Dict[str, float]
            Mapping of income source → total AUD received.
        """
        totals: Dict[str, float] = {}
        for _, amt, src, _ in self._income_ledger:
            totals[src] = totals.get(src, 0.0) + amt
        return totals

    def get_expenses_by_category(self) -> Dict[str, float]:
        """
        Return a dict aggregating total expenses per category.

        Returns
        -------
        Dict[str, float]
            Mapping of expense category → total AUD spent.
        """
        totals: Dict[str, float] = {}
        for _, amt, cat, _ in self._expense_ledger:
            totals[cat] = totals.get(cat, 0.0) + amt
        return totals

    def to_dict(self) -> dict:
        """Serialise state for JSON save/load."""
        return {
            "balance": self.__balance,
            "total_income": self._total_income,
            "total_expenses": self._total_expenses,
            "income_ledger": self._income_ledger,
            "expense_ledger": self._expense_ledger,
        }

    def from_dict(self, data: dict) -> None:
        """Restore state from a plain dict (from JSON)."""
        self.__balance = data.get("balance", self.STARTING_BALANCE)
        self._total_income = data.get("total_income", 0.0)
        self._total_expenses = data.get("total_expenses", 0.0)
        self._income_ledger = [tuple(x) for x in data.get("income_ledger", [])]
        self._expense_ledger = [tuple(x) for x in data.get("expense_ledger", [])]

    def __str__(self) -> str:
        return f"Finance(balance=${self.__balance:,.2f} AUD)"

    def __repr__(self) -> str:
        return (
            f"Finance(balance={self.__balance}, "
            f"total_income={self._total_income}, "
            f"total_expenses={self._total_expenses})"
        )
