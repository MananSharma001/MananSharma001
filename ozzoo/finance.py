"""
finance.py
----------
Finance – Singleton class that tracks all monetary transactions in OzZoo.

Only ONE Finance instance can exist at any time (Singleton pattern).
The singleton is created via __new__ with an _initialised guard so that
__init__ is only executed once even if Finance() is called multiple times.

Accounts for:
  - ticket revenue (animal admissions)
  - food costs
  - vet costs
  - general expenses / income
"""

from __future__ import annotations


class Finance:
    """
    Singleton financial ledger for the entire zoo.

    Pattern: Singleton via __new__ + _initialised guard.

    Attributes (private, read via properties)
    ------------------------------------------
    __balance  : float – current cash balance (AUD)
    __revenue  : float – cumulative ticket / admission revenue
    __expenses : float – cumulative total expenditure
    _initialised: bool  – guards __init__ so it only runs once
    """

    _instance: Finance | None = None
    _initialised: bool = False

    def __new__(cls) -> Finance:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialised:
            return
        self.__balance: float = 50_000.0   # zoo starts with $50,000
        self.__revenue: float = 0.0
        self.__expenses: float = 0.0
        self._initialised = True

    # ------------------------------------------------------------------ #
    #  Properties                                                         #
    # ------------------------------------------------------------------ #

    @property
    def balance(self) -> float:
        return self.__balance

    @property
    def revenue(self) -> float:
        return self.__revenue

    @property
    def expenses(self) -> float:
        return self.__expenses

    # ------------------------------------------------------------------ #
    #  Transactions                                                       #
    # ------------------------------------------------------------------ #

    def charge_admission(self, ticket_price: float, count: int = 1) -> str:
        """Record ticket sales."""
        amount = ticket_price * count
        self.__balance += amount
        self.__revenue += amount
        return f"Admission charged: ${amount:.2f}  |  Balance: ${self.__balance:.2f}"

    def pay_food_bill(self, amount: float) -> str:
        """Deduct food costs."""
        self.__balance -= amount
        self.__expenses += amount
        return f"Food bill paid: ${amount:.2f}  |  Balance: ${self.__balance:.2f}"

    def pay_vet_bill(self, amount: float) -> str:
        """Deduct veterinary costs."""
        self.__balance -= amount
        self.__expenses += amount
        return f"Vet bill paid: ${amount:.2f}  |  Balance: ${self.__balance:.2f}"

    def record_expense(self, description: str, amount: float) -> str:
        """Deduct a general operating expense."""
        self.__balance -= amount
        self.__expenses += amount
        return f"Expense ({description}): ${amount:.2f}  |  Balance: ${self.__balance:.2f}"

    def record_income(self, description: str, amount: float) -> str:
        """Add a non-ticket income (e.g. donations, grants)."""
        self.__balance += amount
        self.__revenue += amount
        return f"Income ({description}): ${amount:.2f}  |  Balance: ${self.__balance:.2f}"

    # ------------------------------------------------------------------ #
    #  Reporting                                                          #
    # ------------------------------------------------------------------ #

    def report(self) -> str:
        profit = self.__revenue - self.__expenses
        return (
            f"=== Finance Report ===\n"
            f"  Balance  : ${self.__balance:,.2f}\n"
            f"  Revenue  : ${self.__revenue:,.2f}\n"
            f"  Expenses : ${self.__expenses:,.2f}\n"
            f"  Net P&L  : ${profit:,.2f}"
        )

    # ------------------------------------------------------------------ #
    #  Singleton reset (for testing only)                                 #
    # ------------------------------------------------------------------ #

    @classmethod
    def reset(cls) -> None:
        """Destroy the singleton so a fresh instance can be created (tests only)."""
        cls._instance = None
        cls._initialised = False

    def __str__(self) -> str:
        return f"Finance(balance=${self.__balance:,.2f})"

    def __repr__(self) -> str:
        return f"Finance(balance={self.__balance!r})"
