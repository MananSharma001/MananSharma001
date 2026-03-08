"""
game_loop.py
============
Provides the ``GameLoop`` class which manages the simulation's time-based
progression independently of the CLI.

Each call to :meth:`GameLoop.tick` advances the zoo by one day, printing
a concise summary of the day's events.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zoo import Zoo


class GameLoop:
    """
    Wraps the Zoo's ``advance_day()`` method with display formatting.

    Parameters
    ----------
    zoo : Zoo
        The zoo instance to advance.
    """

    def __init__(self, zoo: "Zoo") -> None:
        """Initialise the game loop with a Zoo reference."""
        self._zoo: "Zoo" = zoo

    def tick(self) -> str:
        """
        Advance the zoo by one day and return a formatted day summary.

        Returns
        -------
        str
            Multi-line summary of the day's events.
        """
        summary = self._zoo.advance_day()
        lines: list[str] = []

        lines.append(f"\n{'─' * 55}")
        lines.append(f"  📅  Day {summary['day']} — OzZoo Daily Report")
        lines.append(f"{'─' * 55}")
        lines.append(
            f"  🎟️  Visitors: {summary['visitors']}  "
            f"Revenue: ${summary['revenue']:,.2f} AUD"
        )
        lines.append(
            f"  💰  Balance: ${self._zoo.finance.get_balance():,.2f} AUD"
        )

        if summary["animal_events"]:
            lines.append("\n  🐾 Animal Events:")
            for evt in summary["animal_events"][:5]:  # cap to 5 lines
                lines.append(f"     • {evt}")

        if summary["habitat_events"]:
            lines.append("\n  🏡 Habitat Events:")
            for evt in summary["habitat_events"][:3]:
                lines.append(f"     • {evt}")

        if summary["events"]:
            lines.append("\n  📋 Other Events:")
            for evt in summary["events"]:
                lines.append(f"     • {evt}")

        if summary["random_event"]:
            lines.append(f"\n  ⚡  {summary['random_event']}")

        lines.append(f"\n  🏆 Score: {self._zoo.score}")
        lines.append(f"{'─' * 55}")

        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"GameLoop(zoo={self._zoo.name!r}, day={self._zoo.day})"
