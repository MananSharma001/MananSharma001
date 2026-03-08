"""
challenges.py
=============
Daily challenge definitions and tracker for OzZoo.

A new random challenge is generated at the start of each day.  After the
player advances the day the challenge is evaluated; if met, a cash reward
is deposited and a success message is returned.

Each challenge has:
  - ``key``         — template key (reused across days)
  - ``title``       — short display name
  - ``description`` — "what you must do today" sentence
  - ``icon``        — emoji
  - ``reward``      — AUD reward on success
  - ``check``       — callable(zoo, day_summary) → bool
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zoo import Zoo


@dataclass
class ChallengeTemplate:
    """Blueprint for a type of daily challenge."""
    key:         str
    title:       str
    description: str
    icon:        str
    reward:      float
    check:       Callable[["Zoo", dict], bool]


# ---------------------------------------------------------------------------
# Challenge catalogue
# ---------------------------------------------------------------------------

_TEMPLATES: list[ChallengeTemplate] = [
    ChallengeTemplate(
        key="all_fed",
        title="Full Bellies",
        description="End the day with ALL animals at hunger ≤ 20.",
        icon="🍖",
        reward=150,
        check=lambda zoo, s: all(a.hunger <= 20 for a in zoo.get_alive_animals()),
    ),
    ChallengeTemplate(
        key="visitors_40",
        title="Crowd Pleaser",
        description="Welcome at least 40 visitors today.",
        icon="👥",
        reward=200,
        check=lambda zoo, s: s.get("today_visitors", 0) >= 40,
    ),
    ChallengeTemplate(
        key="visitors_55",
        title="Packed House",
        description="Welcome at least 55 visitors today.",
        icon="🎫",
        reward=350,
        check=lambda zoo, s: s.get("today_visitors", 0) >= 55,
    ),
    ChallengeTemplate(
        key="health_avg_80",
        title="Healthy Herd",
        description="End the day with average animal health ≥ 80.",
        icon="💪",
        reward=200,
        check=lambda zoo, s: (
            bool(zoo.get_alive_animals())
            and sum(a.health for a in zoo.get_alive_animals())
            / len(zoo.get_alive_animals()) >= 80
        ),
    ),
    ChallengeTemplate(
        key="happiness_avg_75",
        title="Happy Animals",
        description="End the day with average animal happiness ≥ 75.",
        icon="😊",
        reward=200,
        check=lambda zoo, s: (
            bool(zoo.get_alive_animals())
            and sum(a.happiness for a in zoo.get_alive_animals())
            / len(zoo.get_alive_animals()) >= 75
        ),
    ),
    ChallengeTemplate(
        key="no_deaths",
        title="No Casualties",
        description="End the day with no animal deaths.",
        icon="🛡️",
        reward=100,
        check=lambda zoo, s: s.get("deaths_today", 0) == 0,
    ),
    ChallengeTemplate(
        key="clean_enclosure",
        title="Spick and Span",
        description="Have all enclosures at cleanliness ≥ 60.",
        icon="🧹",
        reward=150,
        check=lambda zoo, s: all(
            enc.cleanliness >= 60 for enc in zoo.enclosures
        ),
    ),
    ChallengeTemplate(
        key="score_up",
        title="Score Climber",
        description="Increase your score compared to yesterday.",
        icon="📈",
        reward=200,
        check=lambda zoo, s: s.get("score_increased", False),
    ),
    ChallengeTemplate(
        key="balance_15k",
        title="Money Bags",
        description="End the day with balance ≥ $15,000.",
        icon="💰",
        reward=300,
        check=lambda zoo, s: zoo.finance.get_balance() >= 15_000,
    ),
    ChallengeTemplate(
        key="species_5",
        title="Diverse Collection",
        description="Have at least 5 different species alive.",
        icon="🦎",
        reward=250,
        check=lambda zoo, s: (
            len({a.species for a in zoo.get_alive_animals()}) >= 5
        ),
    ),
    ChallengeTemplate(
        key="all_healthy",
        title="A+ Animals",
        description="End the day with ALL animals at health ≥ 70.",
        icon="🏥",
        reward=300,
        check=lambda zoo, s: (
            bool(zoo.get_alive_animals())
            and all(a.health >= 70 for a in zoo.get_alive_animals())
        ),
    ),
    ChallengeTemplate(
        key="revenue_1000",
        title="Bumper Day",
        description="Earn at least $1,000 in ticket revenue today.",
        icon="🎟️",
        reward=250,
        check=lambda zoo, s: s.get("today_revenue", 0) >= 1_000,
    ),
]


# ---------------------------------------------------------------------------
# Daily challenge instance
# ---------------------------------------------------------------------------

@dataclass
class DailyChallenge:
    """A specific challenge active for one day."""
    template_key: str
    title:        str
    description:  str
    icon:         str
    reward:       float
    day:          int
    completed:    bool = False
    failed:       bool = False
    _check:       Optional[Callable] = None

    def evaluate(self, zoo: "Zoo", day_summary: dict) -> bool:
        """Return True if the challenge was met."""
        if self._check is None:
            return False
        try:
            return bool(self._check(zoo, day_summary))
        except (AttributeError, KeyError, TypeError, ZeroDivisionError):
            return False  # never crash the game due to a challenge check error


# ---------------------------------------------------------------------------
# Challenge tracker
# ---------------------------------------------------------------------------

class ChallengeTracker:
    """
    Generates and evaluates one daily challenge per day.

    Attributes
    ----------
    _current : Optional[DailyChallenge]
        The challenge active today.
    _history : list[DailyChallenge]
        All past challenges (completed or failed).
    _total_completed : int
        How many challenges the player has completed.
    _total_reward_earned : float
        Total AUD earned from completed challenges.
    """

    def __init__(self) -> None:
        self._current:  Optional[DailyChallenge] = None
        self._history:  list[DailyChallenge]     = []
        self._total_completed:    int   = 0
        self._total_reward_earned: float = 0.0

    # ------------------------------------------------------------------

    def generate_for_day(self, day: int) -> DailyChallenge:
        """
        Pick a random challenge template and make it the active challenge.

        Parameters
        ----------
        day : int
            Current zoo day number.

        Returns
        -------
        DailyChallenge
            The newly generated challenge.
        """
        tmpl = random.choice(_TEMPLATES)
        self._current = DailyChallenge(
            template_key=tmpl.key,
            title=tmpl.title,
            description=tmpl.description,
            icon=tmpl.icon,
            reward=tmpl.reward,
            day=day,
            _check=tmpl.check,
        )
        return self._current

    def evaluate_current(self, zoo: "Zoo", day_summary: dict) -> tuple[bool, float]:
        """
        Evaluate the current challenge.

        Parameters
        ----------
        zoo : Zoo
        day_summary : dict
            The dict returned by zoo.advance_day(), augmented with extra stats.

        Returns
        -------
        tuple[bool, float]
            ``(success, reward_earned)``
        """
        if self._current is None:
            return False, 0.0

        success = self._current.evaluate(zoo, day_summary)
        reward  = 0.0
        if success:
            self._current.completed = True
            reward = self._current.reward
            self._total_completed    += 1
            self._total_reward_earned += reward
        else:
            self._current.failed = True

        self._history.append(self._current)
        self._current = None
        return success, reward

    # ------------------------------------------------------------------

    @property
    def current(self) -> Optional[DailyChallenge]:
        return self._current

    @property
    def total_completed(self) -> int:
        return self._total_completed

    @property
    def total_reward_earned(self) -> float:
        return self._total_reward_earned

    @property
    def recent_history(self) -> list[DailyChallenge]:
        """Last 10 completed/failed challenges."""
        return self._history[-10:]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "total_completed":     self._total_completed,
            "total_reward_earned": self._total_reward_earned,
        }

    def from_dict(self, data: dict) -> None:
        self._total_completed     = data.get("total_completed",     0)
        self._total_reward_earned = data.get("total_reward_earned", 0.0)
