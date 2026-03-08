"""
achievements.py
===============
Achievement definitions and tracker for OzZoo.

Each achievement has:
  - ``key``        — unique string identifier
  - ``title``      — short display name
  - ``description``— what the player must do
  - ``icon``       — emoji shown in the UI
  - ``check``      — callable(zoo, stats) → bool; returns True when unlocked
  - ``reward``     — optional AUD cash reward deposited on unlock

The :class:`AchievementTracker` holds a set of already-unlocked keys and
exposes :meth:`check_all` which returns newly unlocked achievements after
each day advance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zoo import Zoo


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class Achievement:
    """A single unlockable achievement."""
    key:         str
    title:       str
    description: str
    icon:        str
    check:       Callable[["Zoo", dict], bool]
    reward:      float = 0.0


# ---------------------------------------------------------------------------
# Achievement catalogue
# ---------------------------------------------------------------------------

def _make_achievements() -> list[Achievement]:
    return [
        # ── Welfare ────────────────────────────────────────────────────────
        Achievement(
            key="first_feed",
            title="Lunch Time!",
            description="Feed an animal for the first time.",
            icon="🍖",
            check=lambda zoo, s: s.get("total_feeds", 0) >= 1,
            reward=0,
        ),
        Achievement(
            key="full_health",
            title="Peak Condition",
            description="Have all animals at 100 HP simultaneously.",
            icon="💪",
            check=lambda zoo, s: (
                bool(zoo.get_alive_animals())
                and all(a.health == 100 for a in zoo.get_alive_animals())
            ),
            reward=200,
        ),
        Achievement(
            key="welfare_master",
            title="Welfare Master",
            description="Keep average animal health above 90 for 5 consecutive days.",
            icon="🏥",
            check=lambda zoo, s: s.get("high_health_streak", 0) >= 5,
            reward=500,
        ),
        Achievement(
            key="happy_zoo",
            title="Happy Zoo",
            description="Keep average happiness above 80 for 3 consecutive days.",
            icon="😊",
            check=lambda zoo, s: s.get("high_happiness_streak", 0) >= 3,
            reward=300,
        ),
        # ── Animals ────────────────────────────────────────────────────────
        Achievement(
            key="first_birth",
            title="Bundle of Joy",
            description="Breed your first baby animal.",
            icon="🍼",
            check=lambda zoo, s: zoo.animals_born >= 1,
            reward=100,
        ),
        Achievement(
            key="baby_boom",
            title="Baby Boom!",
            description="Have 5 or more animals born total.",
            icon="👶",
            check=lambda zoo, s: zoo.animals_born >= 5,
            reward=300,
        ),
        Achievement(
            key="collector",
            title="Collector",
            description="Own at least 5 different species simultaneously.",
            icon="🦎",
            check=lambda zoo, s: (
                len({a.species for a in zoo.get_alive_animals()}) >= 5
            ),
            reward=500,
        ),
        Achievement(
            key="full_collection",
            title="Full House",
            description="Own all 7 species at the same time.",
            icon="🌟",
            check=lambda zoo, s: (
                len({a.species for a in zoo.get_alive_animals()}) >= 7
            ),
            reward=1000,
        ),
        Achievement(
            key="big_zoo",
            title="Big Zoo",
            description="Have 15 or more living animals.",
            icon="🦁",
            check=lambda zoo, s: len(zoo.get_alive_animals()) >= 15,
            reward=500,
        ),
        # ── Visitors ───────────────────────────────────────────────────────
        Achievement(
            key="first_visitors",
            title="Grand Opening",
            description="Welcome your first visitors.",
            icon="🎉",
            check=lambda zoo, s: zoo.total_visitors >= 1,
            reward=0,
        ),
        Achievement(
            key="popular",
            title="Popular Attraction",
            description="Reach 500 total visitors.",
            icon="👥",
            check=lambda zoo, s: zoo.total_visitors >= 500,
            reward=200,
        ),
        Achievement(
            key="tourist_magnet",
            title="Tourist Magnet",
            description="Reach 2,000 total visitors.",
            icon="🗺️",
            check=lambda zoo, s: zoo.total_visitors >= 2000,
            reward=500,
        ),
        Achievement(
            key="packed_day",
            title="Sold Out!",
            description="Welcome 60 or more visitors in a single day.",
            icon="🎫",
            check=lambda zoo, s: s.get("today_visitors", 0) >= 60,
            reward=200,
        ),
        # ── Finances ───────────────────────────────────────────────────────
        Achievement(
            key="profitable",
            title="In the Black",
            description="Reach a balance of $20,000 AUD.",
            icon="💰",
            check=lambda zoo, s: zoo.finance.get_balance() >= 20_000,
            reward=0,
        ),
        Achievement(
            key="mogul",
            title="Zoo Mogul",
            description="Reach a balance of $50,000 AUD.",
            icon="💎",
            check=lambda zoo, s: zoo.finance.get_balance() >= 50_000,
            reward=1000,
        ),
        # ── Enclosures ─────────────────────────────────────────────────────
        Achievement(
            key="builder",
            title="Master Builder",
            description="Build 2 new enclosures.",
            icon="🏗️",
            check=lambda zoo, s: s.get("enclosures_built", 0) >= 2,
            reward=200,
        ),
        Achievement(
            key="upgrader",
            title="Upgrade Addict",
            description="Upgrade enclosures 5 times total.",
            icon="🔧",
            check=lambda zoo, s: s.get("total_upgrades", 0) >= 5,
            reward=300,
        ),
        # ── Survival ───────────────────────────────────────────────────────
        Achievement(
            key="survivor",
            title="Survivor",
            description="Survive a Disease Outbreak with no animal deaths.",
            icon="🦠",
            check=lambda zoo, s: s.get("outbreak_survived", False),
            reward=400,
        ),
        Achievement(
            key="no_deaths",
            title="No Casualties",
            description="Go 10 days without any animal dying.",
            icon="🛡️",
            check=lambda zoo, s: s.get("no_death_streak", 0) >= 10,
            reward=600,
        ),
        # ── Score ──────────────────────────────────────────────────────────
        Achievement(
            key="score_100",
            title="Rising Star",
            description="Reach a score of 100.",
            icon="⭐",
            check=lambda zoo, s: zoo.score >= 100,
            reward=200,
        ),
        Achievement(
            key="score_200",
            title="Elite Zoo",
            description="Reach a score of 200.",
            icon="🏆",
            check=lambda zoo, s: zoo.score >= 200,
            reward=1000,
        ),
        Achievement(
            key="score_300",
            title="World Class",
            description="Reach a score of 300.",
            icon="🥇",
            check=lambda zoo, s: zoo.score >= 300,
            reward=2000,
        ),
        # ── Longevity ──────────────────────────────────────────────────────
        Achievement(
            key="day_30",
            title="Month in Business",
            description="Run the zoo for 30 days.",
            icon="📅",
            check=lambda zoo, s: zoo.day >= 30,
            reward=500,
        ),
        Achievement(
            key="day_100",
            title="Century!",
            description="Run the zoo for 100 days.",
            icon="💯",
            check=lambda zoo, s: zoo.day >= 100,
            reward=2000,
        ),
    ]


ACHIEVEMENTS: list[Achievement] = _make_achievements()
ACHIEVEMENT_MAP: dict[str, Achievement] = {a.key: a for a in ACHIEVEMENTS}


# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------

class AchievementTracker:
    """
    Tracks which achievements have been unlocked and checks for new ones.

    Attributes
    ----------
    _unlocked : set[str]
        Keys of already-unlocked achievements.
    _stats : dict
        Mutable session statistics used by achievement checks.
    """

    def __init__(self) -> None:
        self._unlocked: set[str] = set()
        self._stats: dict = {
            "total_feeds":           0,
            "total_upgrades":        0,
            "enclosures_built":      0,
            "high_health_streak":    0,
            "high_happiness_streak": 0,
            "no_death_streak":       0,
            "today_visitors":        0,
            "outbreak_survived":     False,
        }

    # ------------------------------------------------------------------
    # Stats update helpers (called from GUI action handlers)
    # ------------------------------------------------------------------

    def record_feed(self) -> None:
        self._stats["total_feeds"] += 1

    def record_upgrade(self) -> None:
        self._stats["total_upgrades"] += 1

    def record_build(self) -> None:
        self._stats["enclosures_built"] += 1

    def record_today_visitors(self, count: int) -> None:
        self._stats["today_visitors"] = count

    def record_outbreak_survived(self) -> None:
        """Call after an outbreak day where no animals died."""
        self._stats["outbreak_survived"] = True

    def update_daily_streaks(self, zoo: "Zoo") -> None:
        """Update streak counters based on end-of-day zoo state.  Call after advance."""
        alive = zoo.get_alive_animals()
        if not alive:
            self._stats["high_health_streak"]    = 0
            self._stats["high_happiness_streak"] = 0
            return
        avg_h  = sum(a.health    for a in alive) / len(alive)
        avg_hp = sum(a.happiness for a in alive) / len(alive)

        if avg_h >= 90:
            self._stats["high_health_streak"] += 1
        else:
            self._stats["high_health_streak"] = 0

        if avg_hp >= 80:
            self._stats["high_happiness_streak"] += 1
        else:
            self._stats["high_happiness_streak"] = 0

    def update_no_death_streak(self, deaths_today: int) -> None:
        if deaths_today == 0:
            self._stats["no_death_streak"] += 1
        else:
            self._stats["no_death_streak"] = 0

    # ------------------------------------------------------------------
    # Core check
    # ------------------------------------------------------------------

    def check_all(self, zoo: "Zoo") -> list[Achievement]:
        """
        Return a list of *newly* unlocked achievements.

        Parameters
        ----------
        zoo : Zoo
            Current zoo instance to pass to each achievement's check function.

        Returns
        -------
        list[Achievement]
            Achievements unlocked for the first time this call.
        """
        newly: list[Achievement] = []
        for ach in ACHIEVEMENTS:
            if ach.key in self._unlocked:
                continue
            try:
                if ach.check(zoo, self._stats):
                    self._unlocked.add(ach.key)
                    newly.append(ach)
            except (AttributeError, KeyError, TypeError, ZeroDivisionError):
                pass  # never crash the game due to an achievement check error
        return newly

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "unlocked": sorted(self._unlocked),
            "stats":    dict(self._stats),
        }

    def from_dict(self, data: dict) -> None:
        self._unlocked = set(data.get("unlocked", []))
        saved = data.get("stats", {})
        self._stats.update(saved)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def unlocked_keys(self) -> set[str]:
        return set(self._unlocked)

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def unlocked_count(self) -> int:
        return len(self._unlocked)

    @property
    def total_count(self) -> int:
        return len(ACHIEVEMENTS)
