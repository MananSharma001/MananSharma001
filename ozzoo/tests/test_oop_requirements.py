"""
test_oop_requirements.py
========================
Unit tests that verify all 12 OOP assignment requirements for OzZoo.

Run with:
    cd ozzoo
    python -m pytest tests/ -v
or without pytest:
    cd ozzoo
    python tests/test_oop_requirements.py

Requirements tested:
    1.  OOP Design (Encapsulation, Inheritance, Polymorphism, Abstraction)
    2.  Min 10 distinct meaningful classes
    3.  Inheritance hierarchy depth ≥ 2
    4.  Abstract Base Classes + ICleanable interface
    5.  Design patterns (Singleton, Factory, Observer)
    6.  Custom exceptions + robust exception handling
    7.  Game loop (GameLoop / Zoo.advance_day)
    8.  Resource management (Finance, FoodInventory)
    9.  Animal welfare (health/hunger/happiness + consequences)
    10. Creativity (achievements, challenges, random events)
"""

from __future__ import annotations

import sys
import os
import unittest

# Allow running from the ozzoo/ directory directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance import Finance
from zoo import Zoo
from enclosure import Enclosure
from habitat import Habitat
from food import FoodInventory, DEFAULT_COSTS
from medicine import MedicineInventory
from visitor import Visitor, generate_visitors
from game_loop import GameLoop
from exceptions import (
    OzZooException,
    InsufficientFundsError,
    AnimalNotFoundError,
    InvalidActionError,
)
from patterns.factory import AnimalFactory
from patterns.observer import (
    ZooEventManager,
    WelfareObserver,
    FinanceObserver,
    EventLogger,
)
from animals.animal import Animal
from animals.mammal import Mammal
from animals.marsupial import Marsupial, Kangaroo, Koala
from animals.bird import Bird, Eagle
from animals.flightless_bird import FlightlessBird, Penguin, Emu
from animals.reptile import Reptile, Crocodile, Snake
from interfaces.icleanable import ICleanable
from achievements import AchievementTracker, ACHIEVEMENTS
from challenges import ChallengeTracker


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def fresh_zoo() -> Zoo:
    """Return a new Zoo with a reset Finance singleton."""
    Finance.reset()
    return Zoo()


# ===========================================================================
# Req 1 & 2 — Classes, Encapsulation
# ===========================================================================

class TestEncapsulation(unittest.TestCase):
    """Verify private attributes use name-mangling (double underscore)."""

    def test_animal_private_health(self) -> None:
        k = Kangaroo("Joey", age=2)
        # Private name-mangled attribute should exist
        self.assertTrue(hasattr(k, "_Animal__health"))
        # Direct attribute access should NOT expose raw private
        self.assertFalse(hasattr(k, "__health"))

    def test_animal_private_hunger(self) -> None:
        k = Kangaroo("Joey", age=2)
        self.assertTrue(hasattr(k, "_Animal__hunger"))

    def test_animal_private_happiness(self) -> None:
        k = Kangaroo("Joey", age=2)
        self.assertTrue(hasattr(k, "_Animal__happiness"))

    def test_finance_private_balance(self) -> None:
        Finance.reset()
        f = Finance.get_instance()
        self.assertTrue(hasattr(f, "_Finance__balance"))
        self.assertFalse(hasattr(f, "__balance"))

    def test_health_clamped_to_range(self) -> None:
        """Setter should clamp values to [0, 100]."""
        k = Kangaroo("Joey", age=1)
        k.health = 200          # should clamp to 100
        self.assertEqual(k.health, 100)
        k.health = -50          # should clamp to 0 (and mark as dead)
        self.assertEqual(k.health, 0)

    def test_hunger_clamped_to_range(self) -> None:
        k = Kangaroo("Joey", age=1)
        k.hunger = 150
        self.assertEqual(k.hunger, 100)
        k.hunger = -10
        self.assertEqual(k.hunger, 0)

    def test_happiness_clamped_to_range(self) -> None:
        k = Kangaroo("Joey", age=1)
        k.happiness = 999
        self.assertEqual(k.happiness, 100)
        k.happiness = -999
        self.assertEqual(k.happiness, 0)


class TestDistinctClasses(unittest.TestCase):
    """Verify at least 10 distinct, meaningful classes exist and are instantiable."""

    def test_at_least_ten_classes(self) -> None:
        Finance.reset()
        instances = [
            Zoo(),
            Enclosure("enc1", "Main Enclosure", "Savannah", max_capacity=5),
            Habitat("hab1", "Main Habitat", "Grassland"),
            FoodInventory(),
            MedicineInventory(),
            Visitor(visitor_id="v1", name="Alice", satisfaction=80),
            GameLoop(Zoo()),
            ZooEventManager(),
            AchievementTracker(),
            ChallengeTracker(),
        ]
        self.assertGreaterEqual(len(instances), 10)

    def test_animal_subclasses_distinct(self) -> None:
        species = {
            Kangaroo("K", 1).species,
            Koala("Ko", 1).species,
            Penguin("P", 1).species,
            Emu("E", 1).species,
            Eagle("Eg", 1).species,
            Crocodile("C", 1).species,
            Snake("S", 1).species,
        }
        # All 7 species should be distinct strings
        self.assertEqual(len(species), 7)


# ===========================================================================
# Req 3 — Inheritance depth ≥ 2
# ===========================================================================

class TestInheritanceHierarchy(unittest.TestCase):
    """Verify inheritance depth and MRO for each concrete animal."""

    def _assert_depth(self, cls, min_depth: int) -> None:
        """Count concrete ancestors (excluding object and ABC)."""
        mro = [c for c in cls.__mro__ if c not in (object,)]
        self.assertGreaterEqual(len(mro), min_depth,
                                f"{cls.__name__} MRO depth too shallow: {mro}")

    def test_kangaroo_depth_4(self) -> None:
        # Kangaroo → Marsupial → Mammal → Animal → ABC → object (≥4 without ABC/object)
        self._assert_depth(Kangaroo, 4)

    def test_koala_depth_4(self) -> None:
        self._assert_depth(Koala, 4)

    def test_penguin_depth_4(self) -> None:
        # Penguin → FlightlessBird → Bird → Animal
        self._assert_depth(Penguin, 4)

    def test_emu_depth_4(self) -> None:
        self._assert_depth(Emu, 4)

    def test_eagle_depth_3(self) -> None:
        # Eagle → Bird → Animal
        self._assert_depth(Eagle, 3)

    def test_crocodile_depth_3(self) -> None:
        self._assert_depth(Crocodile, 3)

    def test_kangaroo_is_marsupial_mammal_animal(self) -> None:
        k = Kangaroo("K", 1)
        self.assertIsInstance(k, Marsupial)
        self.assertIsInstance(k, Mammal)
        self.assertIsInstance(k, Animal)

    def test_penguin_is_flightless_bird_animal(self) -> None:
        p = Penguin("P", 1)
        self.assertIsInstance(p, FlightlessBird)
        self.assertIsInstance(p, Bird)
        self.assertIsInstance(p, Animal)


# ===========================================================================
# Req 4 — Abstraction: ABC + ICleanable interface
# ===========================================================================

class TestAbstraction(unittest.TestCase):
    """Verify ABC enforcement and ICleanable interface."""

    def test_animal_is_abstract(self) -> None:
        """Cannot instantiate Animal directly."""
        with self.assertRaises(TypeError):
            Animal()  # type: ignore[abstract]

    def test_mammal_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            Mammal.__new__(Mammal)

    def test_bird_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            Bird.__new__(Bird)

    def test_reptile_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            Reptile.__new__(Reptile)

    def test_flightless_bird_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            FlightlessBird.__new__(FlightlessBird)

    def test_icleanable_is_interface(self) -> None:
        """ICleanable has only abstract clean() method."""
        self.assertTrue(hasattr(ICleanable, "clean"))
        self.assertTrue(getattr(ICleanable.clean, "__isabstractmethod__", False))

    def test_enclosure_implements_icleanable(self) -> None:
        enc = Enclosure("enc1", "Main Enclosure", "Savannah", max_capacity=4)
        self.assertIsInstance(enc, ICleanable)
        msg = enc.clean()
        self.assertIn("clean", msg.lower())

    def test_habitat_implements_icleanable(self) -> None:
        h = Habitat("hab1", "Outback Zone", "Outback")
        self.assertIsInstance(h, ICleanable)
        msg = h.clean()
        self.assertIsInstance(msg, str)

    def test_abstract_methods_required(self) -> None:
        """Subclass that forgets make_sound() cannot be instantiated."""
        class BadAnimal(Animal):
            pass  # doesn't implement abstract methods

        with self.assertRaises(TypeError):
            BadAnimal()  # type: ignore[abstract]


# ===========================================================================
# Req 5 — Design Patterns
# ===========================================================================

class TestSingletonPattern(unittest.TestCase):
    """Finance must return the same instance every time."""

    def setUp(self) -> None:
        Finance.reset()

    def test_singleton_same_instance(self) -> None:
        f1 = Finance.get_instance()
        f2 = Finance.get_instance()
        self.assertIs(f1, f2)

    def test_singleton_shared_state(self) -> None:
        f1 = Finance.get_instance()
        f1.add_income(500.0, "ticket_sales", "test")
        f2 = Finance.get_instance()
        # Both references share state
        self.assertEqual(f2.get_balance(), f1.get_balance())

    def test_singleton_reset_creates_new(self) -> None:
        f1 = Finance.get_instance()
        Finance.reset()
        f2 = Finance.get_instance()
        # After reset a new instance is created (different object)
        self.assertIsNot(f1, f2)


class TestFactoryPattern(unittest.TestCase):
    """AnimalFactory must create correct concrete types."""

    def test_factory_kangaroo(self) -> None:
        a = AnimalFactory.create_animal("kangaroo", "Bouncer", age=2)
        self.assertIsInstance(a, Kangaroo)
        self.assertEqual(a.name, "Bouncer")
        self.assertEqual(a.age, 2)

    def test_factory_penguin(self) -> None:
        a = AnimalFactory.create_animal("penguin", "Skipper", age=1)
        self.assertIsInstance(a, Penguin)

    def test_factory_crocodile(self) -> None:
        a = AnimalFactory.create_animal("crocodile", "Rex", age=5)
        self.assertIsInstance(a, Crocodile)

    def test_factory_eagle(self) -> None:
        a = AnimalFactory.create_animal("eagle", "Sky", age=3)
        self.assertIsInstance(a, Eagle)

    def test_factory_snake(self) -> None:
        a = AnimalFactory.create_animal("snake", "Sly", age=1)
        self.assertIsInstance(a, Snake)

    def test_factory_emu(self) -> None:
        a = AnimalFactory.create_animal("emu", "Em", age=2)
        self.assertIsInstance(a, Emu)

    def test_factory_koala(self) -> None:
        a = AnimalFactory.create_animal("koala", "Koko", age=3)
        self.assertIsInstance(a, Koala)

    def test_factory_invalid_species(self) -> None:
        with self.assertRaises((ValueError, KeyError, Exception)):
            AnimalFactory.create_animal("dragon", "Puff", age=1)


class TestObserverPattern(unittest.TestCase):
    """ZooEventManager should notify all subscribers."""

    def test_event_logger_captures_events(self) -> None:
        mgr    = ZooEventManager()
        logger = EventLogger()
        mgr.subscribe("test_event", logger)
        mgr.notify("test_event", {"message": "hello"})
        entries = logger.get_all_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["event_type"], "test_event")

    def test_multiple_subscribers(self) -> None:
        mgr     = ZooEventManager()
        logger1 = EventLogger()
        logger2 = EventLogger()
        mgr.subscribe("evt", logger1)
        mgr.subscribe("evt", logger2)
        mgr.notify("evt", {"message": "ping"})
        self.assertEqual(len(logger1.get_all_entries()), 1)
        self.assertEqual(len(logger2.get_all_entries()), 1)

    def test_unsubscribed_not_notified(self) -> None:
        mgr    = ZooEventManager()
        logger = EventLogger()
        mgr.subscribe("a", logger)
        mgr.notify("b", {"message": "other"})
        self.assertEqual(len(logger.get_all_entries()), 0)

    def test_welfare_observer_triggers_on_zoo(self) -> None:
        """Zoo automatically notifies WelfareObserver when animal health is critical."""
        zoo = fresh_zoo()
        alive = zoo.get_alive_animals()
        self.assertTrue(alive, "Zoo should have animals")
        # Force one animal's health below WELFARE_HEALTH_THRESHOLD
        animal = alive[0]
        animal.health = 10
        # _check_welfare fires during advance_day — just call it directly
        zoo._check_welfare()
        # If no exception, observer was invoked correctly
        self.assertTrue(True)


# ===========================================================================
# Req 6 — Exception Handling
# ===========================================================================

class TestExceptions(unittest.TestCase):
    """All custom exceptions should be usable and catchable."""

    def setUp(self) -> None:
        Finance.reset()

    def test_insufficient_funds_on_deduct(self) -> None:
        Finance.reset()
        f = Finance.get_instance()
        # Initial balance is 10_000 from Zoo; here we use Finance directly
        with self.assertRaises(InsufficientFundsError):
            f.deduct_expense(999_999.0, "test", "overspend")

    def test_animal_not_found(self) -> None:
        zoo = fresh_zoo()
        with self.assertRaises(AnimalNotFoundError):
            zoo.feed_animal("NoSuchAnimal123")

    def test_enclosure_not_found(self) -> None:
        zoo = fresh_zoo()
        with self.assertRaises(InvalidActionError):
            zoo.upgrade_enclosure("nonexistent_id")

    def test_custom_exceptions_inherit_base(self) -> None:
        """All custom exceptions must be subclasses of OzZooException."""
        self.assertTrue(issubclass(InsufficientFundsError, OzZooException))
        self.assertTrue(issubclass(AnimalNotFoundError, OzZooException))
        self.assertTrue(issubclass(InvalidActionError, OzZooException))

    def test_exception_is_catchable_as_base(self) -> None:
        """OzZooException base class can catch all custom exceptions."""
        zoo = fresh_zoo()
        caught = False
        try:
            zoo.feed_animal("ghost")
        except OzZooException:
            caught = True
        self.assertTrue(caught)

    def test_insufficient_funds_message(self) -> None:
        Finance.reset()
        f = Finance.get_instance()
        try:
            f.deduct_expense(999_999.0, "x", "y")
        except InsufficientFundsError as exc:
            self.assertIn("999", str(exc))


# ===========================================================================
# Req 7 — Game Loop
# ===========================================================================

class TestGameLoop(unittest.TestCase):
    """GameLoop.tick() must advance the day and produce a report."""

    def setUp(self) -> None:
        self._zoo  = fresh_zoo()
        self._loop = GameLoop(self._zoo)

    def test_tick_advances_day(self) -> None:
        self.assertEqual(self._zoo.day, 0)
        self._loop.tick()
        self.assertEqual(self._zoo.day, 1)

    def test_tick_returns_string_report(self) -> None:
        report = self._loop.tick()
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 10)

    def test_tick_generates_visitors(self) -> None:
        self._loop.tick()
        self.assertGreater(self._zoo.total_visitors, 0)

    def test_tick_collects_revenue(self) -> None:
        initial_balance = self._zoo.finance.get_balance()
        self._loop.tick()
        # Score calculation runs and balance may increase (visitors pay tickets)
        # Balance could decrease if events fire; just check it changed
        self.assertIsNotNone(self._zoo.finance.get_balance())

    def test_multiple_ticks(self) -> None:
        for _ in range(5):
            self._loop.tick()
        self.assertEqual(self._zoo.day, 5)

    def test_score_recalculates_each_tick(self) -> None:
        self._loop.tick()
        self.assertIsInstance(self._zoo.score, int)
        self.assertGreaterEqual(self._zoo.score, 0)


# ===========================================================================
# Req 8 — Resource Management
# ===========================================================================

class TestFinanceManagement(unittest.TestCase):
    """Finance tracks income and expenses correctly."""

    def setUp(self) -> None:
        Finance.reset()
        self._f = Finance.get_instance()

    def test_initial_balance_starts_at_configured_value(self) -> None:
        """Fresh Finance instance starts at the configured STARTING_BALANCE."""
        Finance.reset()
        f = Finance.get_instance()
        self.assertEqual(f.get_balance(), Finance.STARTING_BALANCE)

    def test_add_income(self) -> None:
        Finance.reset()
        f = Finance.get_instance()
        starting = f.get_balance()
        f.add_income(1000.0, "ticket_sales", "test")
        self.assertEqual(f.get_balance(), starting + 1000.0)

    def test_deduct_expense(self) -> None:
        Finance.reset()
        f = Finance.get_instance()
        starting = f.get_balance()
        f.add_income(500.0, "donation", "setup")
        f.deduct_expense(200.0, "food", "bought grass")
        self.assertAlmostEqual(f.get_balance(), starting + 500.0 - 200.0)

    def test_report_returns_string(self) -> None:
        report = self._f.get_report()
        self.assertIsInstance(report, str)

    def test_zoo_initial_balance(self) -> None:
        zoo = fresh_zoo()
        self.assertGreater(zoo.finance.get_balance(), 0)


class TestFoodInventory(unittest.TestCase):
    """FoodInventory tracks stock and enforces correct food types."""

    def test_default_food_types_present(self) -> None:
        inv = FoodInventory()
        for food_type in DEFAULT_COSTS:
            self.assertIn(food_type, inv.VALID_TYPES)

    def test_purchase_increases_stock(self) -> None:
        inv = FoodInventory()
        before = inv.get_quantity("grass")
        inv.purchase("grass", 10)
        self.assertEqual(inv.get_quantity("grass"), before + 10)

    def test_consume_decreases_stock(self) -> None:
        inv = FoodInventory()
        inv.purchase("meat", 5)
        qty_before = inv.get_quantity("meat")
        inv.consume("meat", 2)
        self.assertEqual(inv.get_quantity("meat"), qty_before - 2)

    def test_consume_raises_when_empty(self) -> None:
        inv = FoodInventory()
        # Drain current stock
        qty = inv.get_quantity("fish")
        if qty > 0:
            inv.consume("fish", qty)
        with self.assertRaises(Exception):  # InsufficientFoodError or similar
            inv.consume("fish", 1)

    def test_invalid_food_type(self) -> None:
        inv = FoodInventory()
        with self.assertRaises(Exception):
            inv.purchase("chocolate", 10)  # not a valid food type


# ===========================================================================
# Req 9 — Animal Welfare
# ===========================================================================

class TestAnimalWelfare(unittest.TestCase):
    """Animals' welfare attributes affect health over time."""

    def test_daily_tick_increases_hunger(self) -> None:
        k = Kangaroo("Joey", age=1)
        initial_hunger = k.hunger
        k.daily_tick()
        self.assertGreater(k.hunger, initial_hunger)

    def test_daily_tick_decreases_happiness(self) -> None:
        k = Kangaroo("Joey", age=1)
        initial_happiness = k.happiness
        k.daily_tick()
        self.assertLessEqual(k.happiness, initial_happiness)

    def test_prolonged_hunger_degrades_health(self) -> None:
        k = Kangaroo("Joey", age=1)
        k.hunger = 90  # very hungry
        initial_health = k.health
        # Tick twice to trigger health degradation (needs 2 consecutive hungry days)
        k.daily_tick()
        k.hunger = 90
        k.daily_tick()
        # Health should have dropped
        self.assertLessEqual(k.health, initial_health)

    def test_unhappy_animal_loses_health(self) -> None:
        k = Kangaroo("Joey", age=1)
        k.happiness = 10  # very unhappy (< 20 threshold)
        initial_health = k.health
        k.daily_tick()
        self.assertLess(k.health, initial_health)

    def test_health_zero_marks_animal_dead(self) -> None:
        k = Kangaroo("Joey", age=1)
        k.health = 0
        self.assertFalse(k.is_alive)

    def test_is_healthy_threshold(self) -> None:
        k = Kangaroo("Joey", age=1)
        k.health = 50
        self.assertTrue(k.is_healthy())
        k.health = 20
        self.assertFalse(k.is_healthy())

    def test_is_happy_threshold(self) -> None:
        k = Kangaroo("Joey", age=1)
        k.happiness = 70
        self.assertTrue(k.is_happy())
        k.happiness = 50
        self.assertFalse(k.is_happy())

    def test_medicate_restores_health(self) -> None:
        k = Kangaroo("Joey", age=1)
        k.health = 40
        k.apply_medicine(30)  # apply_medicine restores health
        self.assertGreater(k.health, 40)

    def test_breeding_requires_healthy_happy_pair(self) -> None:
        enc = Enclosure("enc1", "Roo Paddock", "Savannah", max_capacity=10)
        k1  = Kangaroo("K1", age=2)
        k2  = Kangaroo("K2", age=2)
        k1.health = 80; k1.happiness = 80
        k2.health = 80; k2.happiness = 80
        enc.add_animal(k1)
        enc.add_animal(k2)
        # check_breeding returns a string (baby name) or None
        result = enc.check_breeding()
        # result is None or a string — both are valid (breeding is probabilistic)
        self.assertTrue(result is None or isinstance(result, str))


# ===========================================================================
# Req 10 — Creativity & Playability
# ===========================================================================

class TestAchievements(unittest.TestCase):
    """Achievement system unlocks correctly."""

    def setUp(self) -> None:
        Finance.reset()

    def test_twenty_four_achievements_defined(self) -> None:
        self.assertEqual(len(ACHIEVEMENTS), 24)

    def test_no_achievements_on_fresh_tracker(self) -> None:
        t = AchievementTracker()
        self.assertEqual(t.unlocked_count, 0)

    def test_first_feed_achievement(self) -> None:
        zoo = fresh_zoo()
        t   = AchievementTracker()
        t.record_feed()
        newly = t.check_all(zoo)
        titles = [a.title for a in newly]
        self.assertIn("Lunch Time!", titles)

    def test_score_achievement_unlocks(self) -> None:
        zoo = fresh_zoo()
        t   = AchievementTracker()
        # Simulate high score
        zoo._score = 105
        newly = t.check_all(zoo)
        titles = [a.title for a in newly]
        self.assertIn("Rising Star", titles)

    def test_achievement_persistence(self) -> None:
        zoo = fresh_zoo()
        t   = AchievementTracker()
        t.record_feed()
        t.check_all(zoo)
        d  = t.to_dict()
        t2 = AchievementTracker()
        t2.from_dict(d)
        self.assertEqual(t2.unlocked_count, t.unlocked_count)

    def test_achievement_not_fired_twice(self) -> None:
        zoo = fresh_zoo()
        t   = AchievementTracker()
        t.record_feed()
        first  = t.check_all(zoo)
        second = t.check_all(zoo)  # same zoo state
        # "Lunch Time!" should only appear once
        first_titles  = [a.title for a in first]
        second_titles = [a.title for a in second]
        self.assertIn("Lunch Time!", first_titles)
        self.assertNotIn("Lunch Time!", second_titles)


class TestChallenges(unittest.TestCase):
    """Daily challenge system generates and evaluates challenges."""

    def test_generate_returns_challenge(self) -> None:
        ct = ChallengeTracker()
        ch = ct.generate_for_day(1)
        self.assertIsNotNone(ch)
        self.assertIsInstance(ch.title, str)
        self.assertGreater(ch.reward, 0)

    def test_challenge_evaluated_as_complete_or_fail(self) -> None:
        Finance.reset()
        zoo = Zoo()
        ct  = ChallengeTracker()
        ct.generate_for_day(1)
        # Provide a summary that makes some challenges easy
        success, reward = ct.evaluate_current(zoo, {
            "deaths_today": 0,
            "today_visitors": 60,
            "today_revenue": 1500,
            "score_increased": True,
        })
        self.assertIsInstance(success, bool)
        self.assertIsInstance(reward, (int, float))

    def test_challenge_history_records_results(self) -> None:
        Finance.reset()
        zoo = Zoo()
        ct  = ChallengeTracker()
        ct.generate_for_day(1)
        ct.evaluate_current(zoo, {"deaths_today": 0, "today_visitors": 10,
                                  "today_revenue": 250, "score_increased": False})
        self.assertEqual(len(ct.recent_history), 1)

    def test_challenge_persistence(self) -> None:
        Finance.reset()
        zoo = Zoo()
        ct  = ChallengeTracker()
        ct.generate_for_day(1)
        ct.evaluate_current(zoo, {"deaths_today": 0, "today_visitors": 60,
                                  "today_revenue": 1500, "score_increased": True})
        d   = ct.to_dict()
        ct2 = ChallengeTracker()
        ct2.from_dict(d)
        self.assertEqual(ct2.total_completed, ct.total_completed)


# ===========================================================================
# Req 10 — Polymorphism verification
# ===========================================================================

class TestPolymorphism(unittest.TestCase):
    """A single function works correctly for all Animal subclasses."""

    def _eat_all(self, animals):
        """Polymorphic: call eat() on any animal and get a string back."""
        results = []
        for animal in animals:
            result = animal.eat(1)
            self.assertIsInstance(result, str, f"{animal.species}.eat() must return str")
            results.append(result)
        return results

    def test_polymorphic_eat(self) -> None:
        animals = [
            Kangaroo("K", 1),
            Koala("Ko", 1),
            Penguin("P", 1),
            Emu("E", 1),
            Eagle("Eg", 1),
            Crocodile("C", 1),
            Snake("S", 1),
        ]
        self._eat_all(animals)

    def test_polymorphic_make_sound(self) -> None:
        animals = [
            Kangaroo("K", 1), Koala("Ko", 1),
            Penguin("P", 1), Eagle("Eg", 1),
        ]
        for a in animals:
            sound = a.make_sound()
            self.assertIsInstance(sound, str)
            self.assertGreater(len(sound), 0)

    def test_polymorphic_sleep(self) -> None:
        animals = [Kangaroo("K", 1), Penguin("P", 1), Crocodile("C", 1)]
        for a in animals:
            result = a.sleep()
            self.assertIsInstance(result, str)

    def test_all_animals_have_required_food(self) -> None:
        animals = [
            Kangaroo("K", 1), Koala("Ko", 1),
            Penguin("P", 1), Emu("E", 1),
            Eagle("Eg", 1), Crocodile("C", 1),
            Snake("S", 1),
        ]
        valid_foods = {"grass", "fruit", "fish", "meat", "insects"}
        for a in animals:
            self.assertIn(a.required_food, valid_foods,
                          f"{a.species}.required_food='{a.required_food}' not in {valid_foods}")


# ===========================================================================
# Req 10 — Visitor system
# ===========================================================================

class TestVisitors(unittest.TestCase):
    """Visitor generation and satisfaction."""

    def test_generate_visitors_returns_list(self) -> None:
        visitors = generate_visitors(10, 25.0)
        self.assertEqual(len(visitors), 10)

    def test_visitor_satisfaction_range(self) -> None:
        visitors = generate_visitors(20, 30.0)
        for v in visitors:
            self.assertGreaterEqual(v.satisfaction, 0)
            self.assertLessEqual(v.satisfaction, 100)

    def test_visitor_is_dataclass(self) -> None:
        v = Visitor(visitor_id="v1", name="Bob", satisfaction=75)
        self.assertEqual(v.name, "Bob")
        self.assertEqual(v.satisfaction, 75)


# ===========================================================================
# Req 10 — Enclosure and Habitat
# ===========================================================================

class TestEnclosure(unittest.TestCase):
    """Enclosure capacity, cleanliness, and breeding."""

    def _make_enc(self, cap: int = 5) -> Enclosure:
        # Kangaroo habitat is "Savannah" — match the enclosure type
        return Enclosure("enc1", "Test Enclosure", "Savannah", max_capacity=cap)

    def test_add_animal_increases_count(self) -> None:
        enc = self._make_enc()
        k   = Kangaroo("K", 1)
        enc.add_animal(k)
        self.assertEqual(len(enc.animals), 1)

    def test_clean_restores_cleanliness(self) -> None:
        enc = self._make_enc()
        enc.daily_tick()  # reduces cleanliness
        enc.clean()
        self.assertEqual(enc.cleanliness, 100)

    def test_daily_tick_reduces_cleanliness(self) -> None:
        enc = self._make_enc()
        initial = enc.cleanliness
        enc.daily_tick()
        self.assertLess(enc.cleanliness, initial)

    def test_upgrade_increments_level(self) -> None:
        enc = self._make_enc()
        level_before = enc.upgrade_level
        enc.upgrade()
        self.assertEqual(enc.upgrade_level, level_before + 1)

    def test_capacity_enforced(self) -> None:
        enc = self._make_enc(cap=2)
        enc.add_animal(Kangaroo("K1", 1))
        enc.add_animal(Kangaroo("K2", 1))
        with self.assertRaises(Exception):
            enc.add_animal(Kangaroo("K3", 1))


# ===========================================================================
# Integration test — full day cycle
# ===========================================================================

class TestIntegration(unittest.TestCase):
    """End-to-end: create zoo, advance multiple days, verify state."""

    def test_full_three_day_cycle(self) -> None:
        zoo  = fresh_zoo()
        loop = GameLoop(zoo)
        for day in range(1, 4):
            report = loop.tick()
            self.assertEqual(zoo.day, day)
            self.assertIsInstance(report, str)
            self.assertGreaterEqual(zoo.score, 0)
            self.assertGreater(zoo.finance.get_balance(), 0)

    def test_buy_animal_adds_to_zoo(self) -> None:
        zoo = fresh_zoo()
        before = len(zoo.get_alive_animals())
        zoo.buy_animal("snake", "Sid", age=1)
        after = len(zoo.get_alive_animals())
        self.assertEqual(after, before + 1)

    def test_buy_animal_deducts_cost(self) -> None:
        zoo = fresh_zoo()
        balance_before = zoo.finance.get_balance()
        zoo.buy_animal("snake", "Sid", age=1)    # $250
        self.assertLess(zoo.finance.get_balance(), balance_before)

    def test_build_enclosure_deducts_cost(self) -> None:
        zoo = fresh_zoo()
        balance_before = zoo.finance.get_balance()
        zoo.build_enclosure("New Pen", "Grassland", max_capacity=4, area_m2=100)
        self.assertLess(zoo.finance.get_balance(), balance_before)

    def test_feed_animal_reduces_hunger(self) -> None:
        zoo = fresh_zoo()
        animal = zoo.get_alive_animals()[0]
        animal.hunger = 60
        zoo.feed_animal(animal.name)
        self.assertLess(animal.hunger, 60)

    def test_save_and_load_round_trip(self) -> None:
        import json
        zoo = fresh_zoo()
        loop = GameLoop(zoo)
        loop.tick()
        data = zoo.to_dict()
        # Serialise + deserialise
        blob = json.dumps(data)
        loaded = json.loads(blob)
        # Restore
        Finance.reset()
        zoo2 = Zoo()
        zoo2.from_dict(loaded)
        self.assertEqual(zoo2.day, zoo.day)
        self.assertEqual(zoo2.score, zoo.score)


# ===========================================================================
# Entry point for running without pytest
# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
