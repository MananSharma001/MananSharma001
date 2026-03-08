"""
exceptions.py
=============
Custom exception hierarchy for the OzZoo simulation game.

All exceptions inherit from OzZooException so callers can catch either
the base class or the specific sub-class.
"""


class OzZooException(Exception):
    """Base exception for all OzZoo-specific errors."""


class InsufficientFundsError(OzZooException):
    """Raised when an operation cannot proceed due to insufficient zoo funds."""


class HabitatCapacityExceededError(OzZooException):
    """Raised when an enclosure or habitat has reached its animal capacity."""


class IncompatibleSpeciesError(OzZooException):
    """Raised when an animal is placed in an enclosure that does not suit its habitat type."""


class InsufficientFoodError(OzZooException):
    """Raised when there is not enough food stock to feed an animal."""


class AnimalNotFoundError(OzZooException):
    """Raised when a requested animal cannot be located in the zoo."""


class InvalidActionError(OzZooException):
    """Raised when an invalid or logically inconsistent action is requested."""
