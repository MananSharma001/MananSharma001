# OzZoo — Comprehensive Tutorial & Design Document

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Setup & Running the Project](#2-setup--running-the-project)
3. [How to Play (User Guide)](#3-how-to-play-user-guide)
4. [Scoring & Winning](#4-scoring--winning)
5. [UML Class Diagram](#5-uml-class-diagram)
6. [OOP Principles Demonstrated](#6-oop-principles-demonstrated)
7. [Design Patterns](#7-design-patterns)
8. [Exception Handling](#8-exception-handling)
9. [Addictive Gameplay Systems](#9-addictive-gameplay-systems)
10. [Testing](#10-testing)

---

## 1. Project Overview

**OzZoo** is a zoo management simulation game set in Australia.  You are appointed the manager
of a brand-new zoo and must keep your animals healthy, attract visitors, manage resources, and
grow your zoo over time.  The game is implemented in pure Python using:

- **Core simulation:** `zoo.py`, `game_loop.py`, `animals/`, `enclosure.py`, `habitat.py`, `finance.py`
- **GUI:** `gui.py` (tkinter — stdlib only, no extra dependencies)
- **CLI:** `cli.py` (text-based alternative)
- **Gameplay systems:** `achievements.py`, `challenges.py`
- **Design patterns:** `patterns/factory.py`, `patterns/observer.py`
- **Interfaces:** `interfaces/icleanable.py`

---

## 2. Setup & Running the Project

### Requirements

| Requirement | Version |
|---|---|
| Python | ≥ 3.10 |
| tkinter | Included with standard Python on Windows/macOS |

No third-party packages are required.

### Running on Linux / macOS

```bash
cd ozzoo
python main.py          # Auto-selects GUI if tkinter is available, else CLI
python main.py --gui    # Force GUI mode
python main.py --cli    # Force CLI mode
```

### Running on Windows

```powershell
cd ozzoo
python main.py
```

### Running Tests

```bash
cd ozzoo
python tests/test_oop_requirements.py       # Using stdlib unittest
# or with pytest installed:
python -m pytest tests/ -v
```

### Save Files

Games are saved to `ozzoo_save.json` in the working directory.  Load them with the
**📂 Load** button in the GUI or option `[9] Load Game` in the CLI.

---

## 3. How to Play (User Guide)

### 3.1 Starting the Game

When you launch OzZoo you begin with:

| Starting Resource | Value |
|---|---|
| Balance | $10,000 AUD |
| Animals | 8 (2 Kangaroos, 2 Koalas, 2 Penguins, 1 Crocodile, 1 Eagle) |
| Enclosures | 4 (pre-built, matching animal habitats) |
| Ticket price | $25.00 |
| Day | 0 |

### 3.2 The Daily Loop

Each time you press **⏩ Advance Day** (GUI) or **[6] Advance Day** (CLI):

1. Every animal's **hunger increases by +10** and **happiness decreases by -3**
2. Every enclosure **loses 10 cleanliness**
3. Visitors arrive and pay for tickets → revenue deposited
4. A **25% chance** random event fires (Heatwave, Celebration, Escape, Outbreak, Donation, Baby Boom)
5. Breeding check runs for all enclosures with same-species pairs
6. Dead animals (health = 0) are permanently removed
7. Your **Score recalculates**
8. A colour-coded Daily Report popup summarises everything

### 3.3 GUI Tabs Reference

| Tab | What to do here |
|---|---|
| 📊 **Dashboard** | Live KPI tiles (Balance/Day/Animals/Score), welfare bars, Today's Challenge, Streak |
| 🐾 **Animals** | Feed, medicate, move, buy new animals; view individual health bars |
| 🏠 **Enclosures** | Clean, upgrade, build new enclosures |
| 🛒 **Resources** | Buy food (grass/fruit/fish/meat/insects) and medicine |
| 💰 **Finances** | Set ticket price, view ledger, analyse expenses by category |
| 📋 **Event Log** | Colour-coded history of all zoo events |
| 🏅 **Achievements** | Gallery of 24 unlockable achievements + challenge history |

### 3.4 Animal Management

#### Feeding Animals

Animals must be fed regularly.  Each feeding reduces hunger and boosts happiness.

| Trigger | Effect |
|---|---|
| Hunger > 80 for 2 consecutive days | Health −10 per day |
| Happiness < 20 | Health −5 per day |
| Health = 0 | Animal dies permanently |

**Rule of thumb:** Feed animals before hunger exceeds **70**.

#### Medicating Animals

| Medicine | Cost | HP Restored |
|---|---|---|
| Antibiotic | $20/dose | +30 HP |
| Vitamin | $8/dose | +10 HP |
| Painkiller | $12/dose | +15 HP |
| **Vaccine** | **$25/dose** | **+40 HP** ← best value |

#### Buying Animals

| Species | Cost | Habitat | Food |
|---|---|---|---|
| Snake | $250 | Tropical | Insects |
| Emu | $300 | Grassland | Grass |
| Penguin | $350 | Coastal | Fish |
| Koala | $400 | Forest | Fruit/Grass |
| Kangaroo | $500 | Savannah | Grass |
| Eagle | $600 | Savannah | Meat |
| Crocodile | $800 | Wetland | Meat |

#### Breeding

Place two animals of the **same species** in the same enclosure.  Each day there is a
probabilistic chance of a free baby animal being born.

### 3.5 Enclosure Management

- **Clean ($50):** Restores cleanliness to 100.  Enclosures lose 10 cleanliness/day.
  Below 30 cleanliness → animals lose happiness.
- **Upgrade ($500):** +1 level, boosts visitor satisfaction and animal happiness.
- **Build New ($1,000 + $2/m²):** Create a new enclosure.  Habitat type must match the animals you plan to house.

### 3.6 Resource Management

#### Food Prices

| Food | Price/unit | Animals |
|---|---|---|
| Grass | $2.00 | Kangaroo, Koala, Emu |
| Fruit | $3.00 | Koala |
| Insects | $1.50 | Snake |
| Fish | $6.00 | Penguin |
| Meat | $8.00 | Crocodile, Eagle |

### 3.7 Financial Management

**Income sources:**
- Ticket sales: `daily_visitors × ticket_price`
- Event bonuses (Celebration, Donation Drive)
- Achievement rewards ($100–$2,000)
- Daily challenge rewards ($100–$350)
- No-death streak bonuses (every 5 clean days = `streak × $50`)

**Expense categories:**
- Animal purchase · Food · Medicine · Cleaning · Upgrades · Construction · Fines

**Warning thresholds:**
- Balance < $1,000 → LOW FUNDS alert
- Balance = $0 → Cannot purchase anything

### 3.8 Random Events

| Event | Probability | Effect |
|---|---|---|
| 🌡️ Heatwave | 25% chance, 1/6 of events | All animals −5 HP, −10 happiness |
| 🎉 Zoo Celebration | 1/6 | Donation $200–$800 |
| 🚨 Animal Escape | 1/6 | Fine $100–$500 |
| 🦠 Disease Outbreak | 1/6 | One enclosure's animals −10–25 HP |
| 💝 Donation Drive | 1/6 | Donation $300–$2,000 |
| 🍼 Baby Boom | 1/6 | 1–3 free baby animals |

---

## 4. Scoring & Winning

### Score Formula

```
Score = avg_health    × 0.35
      + avg_happiness × 0.25
      + avg_visitor_satisfaction × 0.20
      + unique_species × 5
      + financial_score × 0.20

financial_score = min(100, balance / 1,000 × 10)
```

### Star Ratings

| Score | Stars | Rating |
|---|---|---|
| 0–49 | ★☆☆☆☆ | Struggling |
| 50–109 | ★★☆☆☆ | Average |
| 110–179 | ★★★☆☆ | Good |
| 180–249 | ★★★★☆ | Great |
| 250+ | ★★★★★ | Elite Zoo! |

### Tips for Maximum Score

1. Keep all animals at Health ≥ 70 and Hunger < 30
2. Clean all enclosures every 2–3 days ($50 each)
3. Collect all **7 species** for +35 diversity points
4. Keep balance above $10,000 for max financial score
5. Set ticket price at $25–$30 for optimal visitor flow
6. Complete daily challenges for bonus cash
7. Upgrade enclosures to boost visitor satisfaction

---

## 5. UML Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         INHERITANCE HIERARCHY                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ABC ─────────────────────┐                                                    │
│    │                       │                                                    │
│    ▼                       ▼                                                    │
│   Animal (ABC)           Observer (ABC)            ICleanable (ABC)             │
│   ├── +name: str          ├── WelfareObserver        ├── Enclosure               │
│   ├── +species: str       ├── FinanceObserver        └── Habitat                 │
│   ├── -__health: int      └── EventLogger                                       │
│   ├── -__hunger: int                                                            │
│   ├── -__happiness: int                                                         │
│   ├── +make_sound()* (abstract)                                                 │
│   ├── +eat()* (abstract)                                                        │
│   ├── +sleep()* (abstract)                                                      │
│   ├── +get_info()* (abstract)                                                   │
│   │                                                                             │
│   ├── Mammal (ABC)                                                              │
│   │   └── Marsupial (ABC)                                                       │
│   │       ├── Kangaroo ──── habitat:"Savannah", food:"grass"                   │
│   │       └── Koala ─────── habitat:"Forest",  food:"fruit"                    │
│   │                                                                             │
│   ├── Bird (ABC)                                                                │
│   │   ├── Eagle ──────────── habitat:"Savannah", food:"meat"                   │
│   │   └── FlightlessBird (ABC)                                                  │
│   │       ├── Penguin ────── habitat:"Coastal",  food:"fish"                   │
│   │       └── Emu ────────── habitat:"Grassland",food:"grass"                  │
│   │                                                                             │
│   └── Reptile (ABC)                                                             │
│       ├── Crocodile ──────── habitat:"Wetland",  food:"meat"                   │
│       └── Snake ──────────── habitat:"Tropical", food:"insects"                │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                         COMPOSITION & AGGREGATION                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Zoo ──────────────────────────────────────────────────────────────────────   │
│   ├── +name: str                                                                │
│   ├── +day: int                                                                 │
│   ├── +score: int                                                               │
│   ├── +ticket_price: float                                                      │
│   ├── 1──* Enclosure (composition)                                              │
│   │         ├── +enclosure_id: str                                              │
│   │         ├── +cleanliness: int                                               │
│   │         ├── +upgrade_level: int                                             │
│   │         ├── 0──* Animal (aggregation)                                       │
│   │         ├── +clean()  ◄─── implements ICleanable                           │
│   │         ├── +upgrade()                                                      │
│   │         └── +check_breeding() → Optional[str]                              │
│   │                                                                             │
│   ├── 1──* Habitat (composition)                                                │
│   │         ├── +habitat_id: str                                                │
│   │         └── +clean()  ◄─── implements ICleanable                           │
│   │                                                                             │
│   ├── 1──1 Finance (Singleton)                                                  │
│   │         ├── -__balance: float                                               │
│   │         ├── +add_income()                                                   │
│   │         └── +deduct_expense()                                               │
│   │                                                                             │
│   ├── 1──1 FoodInventory                                                        │
│   │         └── purchase() / consume()                                          │
│   │                                                                             │
│   ├── 1──1 MedicineInventory                                                    │
│   │         └── purchase() / consume()                                          │
│   │                                                                             │
│   └── 1──1 ZooEventManager (Observable)                                        │
│             ├── subscribe(event_type, observer)                                  │
│             └── notify(event_type, data)  ──► observers                         │
│                                                                                  │
│   GameLoop ────────────── uses ────────────► Zoo                                │
│   ├── +tick() → str                                                             │
│   └── (triggers advance_day, events, scoring)                                   │
│                                                                                  │
│   AnimalFactory ─────────── creates ──────► Animal subclasses                  │
│   └── +create_animal(species, name, age)                                        │
│                                                                                  │
│   AchievementTracker ────── observes ─────► Zoo (via check_all)                │
│   ChallengeTracker ──────── generates/eval► DailyChallenge                     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. OOP Principles Demonstrated

### 6.1 Encapsulation

All welfare attributes are **doubly-private** (name-mangled):

```python
# animals/animal.py
class Animal(ABC):
    def __init__(self, ...):
        self.__health:    int = 100   # name-mangled to _Animal__health
        self.__hunger:    int = 0
        self.__happiness: int = 80

    @property
    def health(self) -> int:
        return self.__health

    @health.setter
    def health(self, value: int) -> None:
        self.__health = max(0, min(100, value))  # clamped + validated
        if self.__health == 0:
            self._is_alive = False
```

Similarly, `Finance.__balance` can only be modified through `add_income()` / `deduct_expense()`.

### 6.2 Inheritance

Four-level hierarchy:

```
Animal (ABC)                          ← depth 1
  └── Mammal (ABC)                    ← depth 2
        └── Marsupial (ABC)           ← depth 3
              └── Kangaroo            ← depth 4  (concrete class)
```

```python
# Kangaroo MRO: Kangaroo → Marsupial → Mammal → Animal → ABC → object
>>> [c.__name__ for c in Kangaroo.__mro__]
['Kangaroo', 'Marsupial', 'Mammal', 'Animal', 'ABC', 'object']
```

### 6.3 Polymorphism

A single `feed_animal()` function works for any animal species:

```python
# animals/__init__.py
def feed_animal(animal: Animal, amount: int = 1) -> str:
    return animal.eat(amount)   # dispatches to the correct override at runtime

# zoo.py
def feed_animal(self, name: str) -> str:
    animal = self._find_animal(name)
    food   = animal.required_food
    self.food_inventory.consume(food, 1)    # deduct stock
    return animal.eat(1)                    # polymorphic call
```

Each species has its own `eat()` implementation with different effects on hunger, happiness, and food type consumed.

### 6.4 Abstraction

`Animal` is an ABC with four required abstract methods:

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def eat(self, amount: int = 1) -> str: ...

    @abstractmethod
    def sleep(self) -> str: ...

    @abstractmethod
    def get_info(self) -> str: ...
```

`ICleanable` is a pure interface ABC:

```python
# interfaces/icleanable.py
class ICleanable(ABC):
    @abstractmethod
    def clean(self) -> str: ...
```

Both `Enclosure` and `Habitat` implement `ICleanable`, enforcing the contract at class-definition time.

---

## 7. Design Patterns

### 7.1 Singleton Pattern — `Finance`

**Location:** `finance.py`

**Why chosen:** There must be exactly one source of truth for the zoo's financial state across
all modules.  Multiple `Finance` instances would cause balance inconsistencies.

**Implementation:**

```python
class Finance:
    _instance: Optional["Finance"] = None

    def __new__(cls) -> "Finance":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialised:
            return          # only initialise once
        self.__balance = self.STARTING_BALANCE
        self._initialised = True
```

**Usage:**

```python
fin = Finance.get_instance()   # always returns the same object
fin.add_income(500.0, "ticket_sales", "Day 1 visitors")
```

### 7.2 Factory Pattern — `AnimalFactory`

**Location:** `patterns/factory.py`

**Why chosen:** `Zoo` and the GUI need to create animal objects without hard-coding class
imports everywhere.  Adding a new species requires only adding one entry to `_REGISTRY`.

**Implementation:**

```python
class AnimalFactory:
    _REGISTRY = {
        "kangaroo":  ("animals.marsupial",      "Kangaroo"),
        "koala":     ("animals.marsupial",       "Koala"),
        "penguin":   ("animals.flightless_bird", "Penguin"),
        "emu":       ("animals.flightless_bird", "Emu"),
        "eagle":     ("animals.bird",            "Eagle"),
        "crocodile": ("animals.reptile",         "Crocodile"),
        "snake":     ("animals.reptile",         "Snake"),
    }

    @classmethod
    def create_animal(cls, species: str, name: str, age: int = 1) -> Animal:
        module_path, class_name = cls._REGISTRY[species.lower()]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)(name, age=age)
```

### 7.3 Observer Pattern — `ZooEventManager`

**Location:** `patterns/observer.py`

**Why chosen:** Animal welfare alerts, finance warnings, and the event log all need to react
to state changes deep inside the simulation.  The Observer pattern decouples the publisher
from subscribers.

**Participants:**

| Class | Role |
|---|---|
| `Observer` | Abstract base with `update(event_type, data)` |
| `ZooEventManager` | Maintains `_listeners` dict; calls `notify()` |
| `WelfareObserver` | Prints critical health/happiness alerts to console |
| `FinanceObserver` | Prints low-balance warnings |
| `EventLogger` | Appends all events to an in-memory list for the GUI |

**Flow:**

```
Zoo._check_welfare()
  └── ZooEventManager.notify("animal_health_critical", {"animal": "Skippy", ...})
        ├── WelfareObserver.update(...)  → prints WELFARE ALERT
        └── EventLogger.update(...)      → appends to log
```

---

## 8. Exception Handling

### Custom Exception Hierarchy

```
Exception
└── OzZooException (base for all OzZoo errors)
    ├── InsufficientFundsError     — not enough balance
    ├── InsufficientFoodError      — food stock is empty
    ├── HabitatCapacityExceededError — enclosure is full
    ├── IncompatibleSpeciesError   — animal/habitat type mismatch
    ├── AnimalNotFoundError        — no such animal in zoo
    └── InvalidActionError         — general invalid action
```

### Usage Example

```python
try:
    zoo.feed_animal("Skippy")
except AnimalNotFoundError as exc:
    messagebox.showerror("Error", str(exc))
except InsufficientFoodError as exc:
    messagebox.showerror("No Food", str(exc))
```

---

## 9. Addictive Gameplay Systems

### 9.1 Achievement System (`achievements.py`)

**24 unlockable achievements** across 7 categories:

| Category | Examples |
|---|---|
| Welfare | Lunch Time! (first feed), Peak Condition (all 100 HP), Welfare Master (5-day streak) |
| Animals | Bundle of Joy (first birth), Full House (all 7 species) |
| Visitors | Grand Opening, Sold Out! (60 visitors/day), Tourist Magnet (2,000 total) |
| Finances | In the Black ($20k), Zoo Mogul ($50k) |
| Enclosures | Master Builder, Upgrade Addict |
| Survival | Survivor (outlive outbreak), No Casualties (10-day streak) |
| Score | Rising Star (100), Elite Zoo (200), World Class (300) |

Each achievement deposits a cash reward when unlocked.  Achievements are checked after every
day advance and fire animated toast notifications.

### 9.2 Daily Challenge System (`challenges.py`)

A random challenge is generated before each day advance.  Completing it earns bonus cash.
12 challenge templates include: Full Bellies, Crowd Pleaser, Healthy Herd, Money Bags, etc.

### 9.3 No-Death Streak Bonuses

Every 5 consecutive days without an animal death: `streak × $50 AUD` bonus + toast notification.

### 9.4 Personal Best Tracking

Best-ever score is saved in the save file.  A "New personal best!" toast fires when beaten.

### 9.5 News Ticker

A scrolling marquee in the header shows recent events, challenge completions, and achievements.

---

## 10. Testing

The test suite lives in `ozzoo/tests/test_oop_requirements.py`.

### Running

```bash
cd ozzoo
python tests/test_oop_requirements.py -v   # stdlib unittest
```

### Coverage

| Test Class | Tests | Requirement Covered |
|---|---|---|
| `TestEncapsulation` | 7 | Req 2 — Private attributes + clamping |
| `TestDistinctClasses` | 2 | Req 2 — ≥10 classes |
| `TestInheritanceHierarchy` | 8 | Req 3 — Depth ≥ 2 |
| `TestAbstraction` | 9 | Req 4 — ABCs + ICleanable |
| `TestSingletonPattern` | 3 | Req 5 — Singleton |
| `TestFactoryPattern` | 8 | Req 5 — Factory |
| `TestObserverPattern` | 4 | Req 5 — Observer |
| `TestExceptions` | 6 | Req 6 — Custom exceptions |
| `TestGameLoop` | 6 | Req 7 — Game loop |
| `TestFinanceManagement` | 5 | Req 8 — Finance |
| `TestFoodInventory` | 5 | Req 8 — Food resources |
| `TestAnimalWelfare` | 9 | Req 9 — Welfare system |
| `TestAchievements` | 6 | Req 10 — Achievements |
| `TestChallenges` | 4 | Req 10 — Daily challenges |
| `TestPolymorphism` | 4 | Req 1 — Polymorphism |
| `TestVisitors` | 3 | Req 10 — Visitor system |
| `TestEnclosure` | 5 | Req 9 — Enclosures |
| `TestIntegration` | 6 | All — End-to-end |
| **Total** | **100** | |

All 100 tests pass with `OK`.
