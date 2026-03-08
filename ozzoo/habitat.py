"""
habitat.py
==========
Defines the ``Habitat`` class — a broader geographical zone that can
contain one or more ``Enclosure`` objects.

``Habitat`` implements :class:`~interfaces.icleanable.ICleanable`.
"""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from interfaces.icleanable import ICleanable

if TYPE_CHECKING:
    from enclosure import Enclosure


class Habitat(ICleanable):
    """
    Represents a named habitat zone in the zoo (e.g. ``"Australian Outback"``).

    A habitat groups related enclosures and provides zone-level management
    such as cleaning all enclosures in the zone at once.

    Parameters
    ----------
    habitat_id : str
        Unique identifier.
    name : str
        Human-readable zone name.
    habitat_type : str
        The environment type (e.g. ``"Savannah"``, ``"Arctic"``, ``"Wetlands"``).
    description : str
        Short description of the habitat.
    """

    TEMPERATURE_DEFAULTS: dict[str, float] = {
        "Savannah": 28.0,
        "Arctic": -5.0,
        "Wetlands": 25.0,
        "Forest": 20.0,
        "Desert": 35.0,
        "Ocean": 18.0,
    }

    def __init__(
        self,
        habitat_id: str,
        name: str,
        habitat_type: str,
        description: str = "",
    ) -> None:
        """Initialise the habitat with default temperature and no enclosures."""
        self._habitat_id: str = habitat_id
        self._name: str = name
        self._habitat_type: str = habitat_type
        self._description: str = description
        self._enclosures: List["Enclosure"] = []
        self.__temperature: float = self.TEMPERATURE_DEFAULTS.get(habitat_type, 20.0)
        self.__cleanliness: int = 100

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def habitat_id(self) -> str:
        """Unique habitat identifier."""
        return self._habitat_id

    @property
    def name(self) -> str:
        """Human-readable zone name."""
        return self._name

    @property
    def habitat_type(self) -> str:
        """The environment type simulated by this habitat."""
        return self._habitat_type

    @property
    def temperature(self) -> float:
        """Current ambient temperature in °C."""
        return self.__temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set the ambient temperature (clamped to realistic range)."""
        self.__temperature = max(-30.0, min(60.0, value))

    @property
    def cleanliness(self) -> int:
        """Overall habitat cleanliness (0-100)."""
        return self.__cleanliness

    @property
    def enclosures(self) -> List["Enclosure"]:
        """List of enclosures in this habitat."""
        return list(self._enclosures)

    # ------------------------------------------------------------------
    # Enclosure management
    # ------------------------------------------------------------------

    def add_enclosure(self, enclosure: "Enclosure") -> str:
        """
        Add an enclosure to this habitat.

        Parameters
        ----------
        enclosure : Enclosure
            The enclosure to register.

        Returns
        -------
        str
            Confirmation message.
        """
        self._enclosures.append(enclosure)
        return f"Enclosure '{enclosure.name}' added to habitat '{self._name}'."

    def get_enclosure_by_id(self, enclosure_id: str) -> Optional["Enclosure"]:
        """
        Find and return an enclosure by its ID.

        Parameters
        ----------
        enclosure_id : str
            The ID to search for.

        Returns
        -------
        Optional[Enclosure]
            The matching enclosure, or ``None`` if not found.
        """
        for enc in self._enclosures:
            if enc.enclosure_id == enclosure_id:
                return enc
        return None

    # ------------------------------------------------------------------
    # ICleanable implementation
    # ------------------------------------------------------------------

    def clean(self) -> str:
        """
        Clean the entire habitat zone, including all enclosures.

        Returns
        -------
        str
            A summary of the cleaning action.
        """
        self.__cleanliness = 100
        messages = [f"🌿 Habitat '{self._name}' has been cleaned!"]
        for enc in self._enclosures:
            messages.append(enc.clean())
        return "\n".join(messages)

    # ------------------------------------------------------------------
    # Daily simulation
    # ------------------------------------------------------------------

    def daily_tick(self) -> list[str]:
        """
        Simulate one day passing in this habitat.

        Returns
        -------
        list[str]
            Event messages for the day.
        """
        events: list[str] = []
        self.__cleanliness = max(0, self.__cleanliness - 5)
        for enc in self._enclosures:
            events.extend(enc.daily_tick())
        return events

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_summary(self) -> str:
        """
        Return a formatted summary of this habitat and its enclosures.

        Returns
        -------
        str
            Multi-line summary string.
        """
        enc_summary = "\n".join(
            f"   {enc.get_summary()}" for enc in self._enclosures
        ) or "   (no enclosures)"
        return (
            f"🌍 Habitat: {self._name} (ID: {self._habitat_id})\n"
            f"   Type        : {self._habitat_type}\n"
            f"   Temperature : {self.__temperature:.1f}°C\n"
            f"   Cleanliness : {self.__cleanliness}/100\n"
            f"   Description : {self._description}\n"
            f"   Enclosures  :\n{enc_summary}"
        )

    def __str__(self) -> str:
        return (
            f"Habitat({self._name!r}, {self._habitat_type}, "
            f"{len(self._enclosures)} enclosure(s), "
            f"temp={self.__temperature:.1f}°C)"
        )

    def __repr__(self) -> str:
        return (
            f"Habitat(id={self._habitat_id!r}, name={self._name!r}, "
            f"habitat_type={self._habitat_type!r})"
        )
