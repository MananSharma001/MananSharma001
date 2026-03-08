# OzZoo — Design Notes

## 1. Design Patterns

### 1.1 Observer Pattern

**Location:** `patterns/observer.py`

**Why chosen:**
Animal welfare monitoring and financial alerts need to react to state changes deep inside the
simulation without coupling those modules to the notification code.  The Observer (aka
Publish-Subscribe) pattern decouples the publisher (`ZooEventManager`) from all subscribers.

**Code flow:**
```
Zoo._check_welfare()
  └── ZooEventManager.notify("animal_health_critical", {...})
        ├── WelfareObserver.update(...)  → prints console alert
        └── EventLogger.update(...)      → appends to log list
```

**Participants:**
- `Observer` — abstract base class with `update(event_type, data)` interface
- `ZooEventManager` — maintains `_listeners` dict, calls `notify()`
- `WelfareObserver` — concrete observer for health events
- `FinanceObserver` — concrete observer for finance events
- `EventLogger` — logs all events to a list

---

### 1.2 Factory Pattern

**Location:** `patterns/factory.py`

**Why chosen:**
The CLI and `Zoo` class need to create animals without knowing the concrete class hierarchy.
The Factory pattern centralises this responsibility and makes extending the species list trivial.

**Code flow:**
```
AnimalFactory.create_animal("penguin", "Percy", age=2)
  └── importlib.import_module("animals.flightless_bird")
        └── Penguin(name="Percy", age=2)
```

**Adding a new species:**
1. Create the class in the appropriate `animals/` module.
2. Add one entry to `AnimalFactory._REGISTRY`.

---

### 1.3 Singleton Pattern

**Location:** `finance.py`

**Why chosen:**
There must be exactly one source of truth for the zoo's financial state.  Multiple `Finance`
instances would create inconsistency.

**Implementation:**
```python
class Finance:
    _instance: Optional["Finance"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Usage:**
```python
fin = Finance.get_instance()   # always returns the same object
fin.add_income(500.0, "ticket_sales")
```

---

## 2. OOP Principles Demonstrated

### 2.1 Encapsulation

All welfare attributes on `Animal` are **private** (`__health`, `__hunger`, `__happiness`) and
accessed via `@property` / `@setter` decorators with built-in validation (clamping to [0,100]).

`Finance.__balance` is likewise private — external code cannot set it directly, only through
`add_income()` and `deduct_expense()`.

### 2.2 Inheritance

```
Animal (ABC)
├── Mammal (ABC)            depth 2
│   └── Marsupial (ABC)    depth 3
│       ├── Kangaroo       depth 4  ← concrete
│       └── Koala          depth 4  ← concrete
├── Bird (ABC)              depth 2
│   └── FlightlessBird     depth 3  ← abstract
│       ├── Penguin        depth 4  ← concrete
│       └── Emu            depth 4  ← concrete
└── Reptile (ABC)           depth 2
    ├── Crocodile           depth 3  ← concrete
    └── Snake               depth 3  ← concrete
```

### 2.3 Polymorphism

The `feed_animal(animal)` function in `animals/__init__.py` accepts *any* `Animal` subclass and
calls the correct `eat()` override at runtime:

```python
def feed_animal(animal: Animal, amount: int = 1) -> str:
    return animal.eat(amount)   # polymorphic dispatch
```

Each concrete class implements `eat()` differently:
- `Kangaroo.eat()` — consumes grass, -20 hunger, +5 happiness
- `Penguin.eat()` — consumes fish, -20 hunger, +8 happiness
- `Crocodile.eat()` — consumes meat, -25 hunger, +8 happiness

### 2.4 Abstraction

`Animal` is an **ABC** with four abstract methods: `make_sound()`, `eat()`, `sleep()`, and
`get_info()`.  Python's `abc.ABC` + `@abstractmethod` enforce this contract at class definition
time — you cannot instantiate `Animal` directly.

`ICleanable` is a pure interface ABC with a single abstract method `clean()`, implemented by
both `Enclosure` and `Habitat`.

---

## 3. Class Hierarchy Diagram

```
object
└── ABC
    ├── Animal          (animals/animal.py)
    │   ├── Mammal      (animals/mammal.py)
    │   │   └── Marsupial (animals/marsupial.py)
    │   │       ├── Kangaroo
    │   │       └── Koala
    │   ├── Bird        (animals/bird.py)
    │   │   ├── Eagle
    │   │   └── FlightlessBird (animals/flightless_bird.py)
    │   │       ├── Penguin
    │   │       └── Emu
    │   └── Reptile     (animals/reptile.py)
    │       ├── Crocodile
    │       └── Snake
    ├── Observer        (patterns/observer.py)
    │   ├── WelfareObserver
    │   ├── FinanceObserver
    │   └── EventLogger
    └── ICleanable      (interfaces/icleanable.py)
        ├── Enclosure   (enclosure.py)
        └── Habitat     (habitat.py)

Finance (Singleton)     (finance.py)
Zoo                     (zoo.py)
GameLoop                (game_loop.py)
CLI                     (cli.py)
AnimalFactory           (patterns/factory.py)
FoodInventory           (food.py)
MedicineInventory       (medicine.py)
Visitor (dataclass)     (visitor.py)
FoodItem (dataclass)    (food.py)
MedicineItem (dataclass)(medicine.py)
```

---

## 4. Key Design Decisions and Trade-offs

### Decision 1 — ABC vs Protocol for ICleanable

**Chose:** `ABC` with `@abstractmethod`
**Alternative:** `typing.Protocol`
**Reason:** ABC enforces the contract at class definition time (raises `TypeError` if `clean()`
is not implemented).  Protocol is structural and checked only by type checkers like `mypy`.
Since this is an educational project, explicit ABC enforcement is more instructive.

### Decision 2 — Singleton via `__new__`

**Chose:** Override `__new__` + guard flag `_initialised`
**Alternative:** Module-level global instance
**Reason:** A class-based singleton is more Pythonic and testable (the `reset()` class method
lets tests start fresh).

### Decision 3 — FoodInventory vs individual Food objects

**Chose:** A single `FoodInventory` class managing all food types in a dict
**Alternative:** One `Food` object per food type, held in a list
**Reason:** The inventory pattern is more efficient for lookup and reporting, and reduces object
count significantly.

### Decision 4 — Lazy imports in AnimalFactory

**Chose:** `importlib.import_module()` inside `create_animal()`
**Alternative:** Top-level `from animals.marsupial import Kangaroo, ...`
**Reason:** Avoids circular imports at module load time (e.g. `Zoo` → `AnimalFactory` →
`animals.*` → `Animal` → `exceptions` is fine, but other import chains could become circular).

### Decision 5 — Dataclasses for Visitor, FoodItem, MedicineItem

**Chose:** `@dataclass`
**Alternative:** Plain classes with `__init__`
**Reason:** Dataclasses provide `__repr__`, `__eq__` and concise syntax for value objects that
primarily store data.

---

## 5. AI Copilot Usage Log Template

| Date | Tool | Prompt | File(s) Affected | Changes Accepted | Changes Rejected |
|---|---|---|---|---|---|
| 2025-xx-xx | GitHub Copilot | "Create observer pattern" | patterns/observer.py | Full draft | Minor naming changes |
| 2025-xx-xx | GitHub Copilot | "Type hints for Zoo class" | zoo.py | All hints | — |

*Fill in above with actual usage during development.*
