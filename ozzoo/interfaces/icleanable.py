"""
interfaces/icleanable.py
========================
Defines the ICleanable interface that any zoo structure which can be
cleaned (Enclosure, Habitat) must implement.
"""

from abc import ABC, abstractmethod


class ICleanable(ABC):
    """
    Interface for objects that can be cleaned.

    Any class that manages a physical space in the zoo should implement
    this interface to ensure consistent cleanliness tracking.
    """

    @abstractmethod
    def clean(self) -> str:
        """
        Perform a cleaning action on this object.

        Returns
        -------
        str
            A message describing the result of the cleaning action.
        """
