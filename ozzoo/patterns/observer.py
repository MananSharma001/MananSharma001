"""
patterns/observer.py
====================
Implements the **Observer** (Publish-Subscribe) design pattern for the
OzZoo simulation.

Components
----------
- ``Observer``          – Abstract base observer interface.
- ``ZooEventManager``   – The subject/publisher that manages subscriptions
                          and broadcasts events.
- ``WelfareObserver``   – Reacts to animal-health events.
- ``FinanceObserver``   – Reacts to low-funds events.
- ``EventLogger``       – Logs every event to an in-memory list.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Abstract Observer interface
# ---------------------------------------------------------------------------

class Observer(ABC):
    """Abstract base class for all event observers in OzZoo."""

    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Called by the publisher when an event occurs.

        Parameters
        ----------
        event_type : str
            A short identifier for the event (e.g. ``"animal_health_critical"``).
        data : Dict[str, Any]
            Arbitrary key-value pairs carrying event-specific payload.
        """


# ---------------------------------------------------------------------------
# Subject / Publisher
# ---------------------------------------------------------------------------

class ZooEventManager:
    """
    Central event publisher for the zoo.

    Observers can subscribe to one or more named event types.  When the
    zoo raises an event, all subscribed observers are notified in the
    order they registered.

    Attributes
    ----------
    _listeners : Dict[str, List[Observer]]
        Mapping from event type string to list of subscribed observers.
    """

    def __init__(self) -> None:
        """Initialise with an empty listener registry."""
        self._listeners: Dict[str, List[Observer]] = {}

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def subscribe(self, event_type: str, observer: Observer) -> None:
        """
        Subscribe *observer* to *event_type*.

        Parameters
        ----------
        event_type : str
            The event identifier to subscribe to.
        observer : Observer
            The observer instance to register.
        """
        self._listeners.setdefault(event_type, [])
        if observer not in self._listeners[event_type]:
            self._listeners[event_type].append(observer)

    def unsubscribe(self, event_type: str, observer: Observer) -> None:
        """
        Remove *observer* from *event_type* subscribers.

        Parameters
        ----------
        event_type : str
            The event identifier to unsubscribe from.
        observer : Observer
            The observer instance to remove.
        """
        if event_type in self._listeners:
            self._listeners[event_type].remove(observer)

    # ------------------------------------------------------------------
    # Event broadcasting
    # ------------------------------------------------------------------

    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcast *event_type* to all registered observers.

        Parameters
        ----------
        event_type : str
            The event identifier to broadcast.
        data : Dict[str, Any]
            Payload to pass to each observer's ``update`` method.
        """
        for observer in self._listeners.get(event_type, []):
            observer.update(event_type, data)

    def notify_all(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Convenience alias for :meth:`notify`.

        Parameters
        ----------
        event_type : str
            The event identifier.
        data : Dict[str, Any]
            Payload to pass to each observer.
        """
        self.notify(event_type, data)

    def __repr__(self) -> str:
        return f"ZooEventManager(event_types={list(self._listeners.keys())})"


# ---------------------------------------------------------------------------
# Concrete Observers
# ---------------------------------------------------------------------------

class WelfareObserver(Observer):
    """
    Monitors animal welfare events.

    Triggers a console alert whenever an animal's health drops below the
    critical threshold (< 30).

    Attributes
    ----------
    _alerts : List[str]
        History of welfare alert messages generated.
    """

    CRITICAL_HEALTH: int = 30

    def __init__(self) -> None:
        """Initialise with an empty alert history."""
        self._alerts: List[str] = []

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle an incoming welfare event.

        Parameters
        ----------
        event_type : str
            Expected to be ``"animal_health_critical"`` or similar.
        data : Dict[str, Any]
            Should contain keys ``"animal_name"`` and ``"health"``.
        """
        animal_name = data.get("animal_name", "Unknown Animal")
        health = data.get("health", 0)
        msg = (
            f"[WELFARE ALERT] {animal_name} has critically low health: "
            f"{health}/100!  Immediate attention required."
        )
        self._alerts.append(msg)
        print(msg)

    @property
    def alerts(self) -> List[str]:
        """Return the list of recorded welfare alerts."""
        return list(self._alerts)

    def __repr__(self) -> str:
        return f"WelfareObserver(alert_count={len(self._alerts)})"


class FinanceObserver(Observer):
    """
    Monitors financial events and warns when funds are critically low.

    Attributes
    ----------
    _threshold : float
        Balance level below which a warning is triggered.
    _warnings : List[str]
        History of financial warnings.
    """

    def __init__(self, threshold: float = 1000.0) -> None:
        """
        Initialise the finance observer.

        Parameters
        ----------
        threshold : float
            Balance threshold in AUD.  Defaults to $1,000.
        """
        self._threshold = threshold
        self._warnings: List[str] = []

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle an incoming finance event.

        Parameters
        ----------
        event_type : str
            Expected to be ``"low_funds"`` or similar.
        data : Dict[str, Any]
            Should contain key ``"balance"``.
        """
        balance = data.get("balance", 0.0)
        msg = (
            f"[FINANCE ALERT] Funds are critically low: "
            f"${balance:,.2f} AUD (threshold: ${self._threshold:,.2f})"
        )
        self._warnings.append(msg)
        print(msg)

    @property
    def warnings(self) -> List[str]:
        """Return the list of recorded financial warnings."""
        return list(self._warnings)

    def __repr__(self) -> str:
        return (
            f"FinanceObserver(threshold=${self._threshold:.2f}, "
            f"warning_count={len(self._warnings)})"
        )


class EventLogger(Observer):
    """
    Logs every zoo event to an in-memory list with timestamps.

    Attributes
    ----------
    _log : List[Dict[str, Any]]
        Ordered list of recorded events; each entry is a dict with keys
        ``"timestamp"``, ``"event_type"``, and ``"data"``.
    """

    def __init__(self) -> None:
        """Initialise with an empty event log."""
        self._log: List[Dict[str, Any]] = []

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Record an event in the log.

        Parameters
        ----------
        event_type : str
            Identifier for the event.
        data : Dict[str, Any]
            Arbitrary event payload.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
        }
        self._log.append(entry)

    @property
    def log(self) -> List[Dict[str, Any]]:
        """Return a copy of the event log."""
        return list(self._log)

    def get_recent(self, n: int = 10) -> List[str]:
        """
        Return the *n* most recent log entries as formatted strings.

        Parameters
        ----------
        n : int
            Number of entries to return.  Defaults to 10.

        Returns
        -------
        List[str]
            Human-readable log lines, most recent last.
        """
        recent = self._log[-n:]
        return [
            f"[{e['timestamp']}] {e['event_type'].upper()}: {e['data']}"
            for e in recent
        ]

    def clear(self) -> None:
        """Clear all log entries."""
        self._log.clear()

    def __repr__(self) -> str:
        return f"EventLogger(entry_count={len(self._log)})"
