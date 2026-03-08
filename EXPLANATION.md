# OzZoo – Complete Program Explanation

> **OzZoo** is an object-oriented Python simulation of a virtual zoo.  
> It demonstrates **encapsulation**, **inheritance**, **polymorphism**, **abstract classes**, and the **Singleton** design pattern.

---

## Table of Contents

1. [Directory Structure](#1-directory-structure)  
2. [How the Program Works – High-Level Flow](#2-how-the-program-works)  
3. [All Classes at a Glance](#3-all-classes-at-a-glance)  
4. [Inheritance Hierarchy (with diagram)](#4-inheritance-hierarchy)  
5. [Class-by-Class Deep Dive](#5-class-by-class-deep-dive)  
   - [Animal (ABC)](#51-animal-abc--abstract-base-class)  
   - [Mammal](#52-mammal)  
   - [Bird](#53-bird)  
   - [Reptile](#54-reptile)  
   - [Lion](#55-lion)  
   - [Elephant](#56-elephant)  
   - [Eagle](#57-eagle)  
   - [Parrot](#58-parrot)  
   - [Crocodile](#59-crocodile)  
   - [Gecko](#510-gecko)  
   - [Habitat](#511-habitat)  
   - [Finance](#512-finance-singleton)  
   - [Zoo](#513-zoo)  
6. [Habitat – Everything You Need to Know](#6-habitat--everything-you-need-to-know)  
7. [OOP Concepts Used](#7-oop-concepts-used)  
8. [Running the Program](#8-running-the-program)  

---

## 1. Directory Structure

```
ozzoo/
├── __init__.py          ← marks ozzoo as a Python package
├── main.py              ← entry point / demo script
├── habitat.py           ← Habitat class
├── finance.py           ← Finance singleton class
├── zoo.py               ← Zoo orchestrator class
└── animals/
    ├── __init__.py      ← re-exports all animal classes
    ├── animal.py        ← Animal abstract base class
    ├── mammal.py        ← Mammal (intermediate)
    ├── bird.py          ← Bird (intermediate)
    ├── reptile.py       ← Reptile (intermediate)
    ├── lion.py          ← Lion (concrete)
    ├── elephant.py      ← Elephant (concrete)
    ├── eagle.py         ← Eagle (concrete)
    ├── parrot.py        ← Parrot (concrete)
    ├── crocodile.py     ← Crocodile (concrete)
    └── gecko.py         ← Gecko (concrete)
```

**Total files:** 13  
**Total classes:** 13 (one per file)

---

## 2. How the Program Works

```
main.py
  │
  ├─► Create Zoo  ──────────────────────────────────────┐
  │                                                     │
  ├─► Create Habitats (Savannah, Aviary, Reptile House) │  Zoo owns
  │       │                                             │  habitats &
  │       └─► Zoo.add_habitat(habitat)                  │  delegates to
  │                                                     │  Finance
  ├─► Create Animals (Lion, Elephant, Eagle, …)         │
  │       │                                             │
  │       └─► Zoo.place_animal(animal, habitat_name)    │
  │               └─► Habitat.add_animal(animal)        │
  │                                                     │
  ├─► Interact with animals                             │
  │       │                                             │
  │       └─► animal.feed() / play() / sound() / …     │
  │                                                     │
  ├─► Zoo.admit_visitors(count=100)                     │
  │       └─► Finance.charge_admission(price, count)    │
  │                                                     │
  ├─► Zoo.simulate_day()                                │
  │       └─► Habitat.simulate_day() for each habitat   │
  │                                                     │
  └─► Zoo.full_report()
          └─► Habitat.report() + Finance.report()
```

### Step-by-step execution

| Step | What happens |
|------|-------------|
| 1 | A `Zoo` object is created. It immediately acquires the `Finance` singleton. |
| 2 | Three `Habitat` objects are created and registered with the zoo. |
| 3 | Animal objects (Lion, Elephant, Eagle, Parrot, Crocodile, Gecko) are instantiated. |
| 4 | Each animal is placed into an appropriate habitat via `Zoo.place_animal()`. |
| 5 | Animal-specific actions are called (`hunt`, `fly`, `dive`, `talk`, `bask`, etc.). |
| 6 | 100 visitors are admitted; ticket revenue flows into `Finance`. |
| 7 | A day is simulated: hunger increases, reptiles bask, aquatic animals get a happiness boost, operating costs are deducted. |
| 8 | A full report is printed: all habitat statuses + financial summary. |

---

## 3. All Classes at a Glance

| # | Class | File | Type | Inherits from |
|---|-------|------|------|---------------|
| 1 | `Animal` | `animals/animal.py` | Abstract base class (ABC) | `ABC` (from `abc` module) |
| 2 | `Mammal` | `animals/mammal.py` | Intermediate / concrete | `Animal` |
| 3 | `Bird` | `animals/bird.py` | Intermediate / concrete | `Animal` |
| 4 | `Reptile` | `animals/reptile.py` | Intermediate / concrete | `Animal` |
| 5 | `Lion` | `animals/lion.py` | Concrete (leaf) | `Mammal` |
| 6 | `Elephant` | `animals/elephant.py` | Concrete (leaf) | `Mammal` |
| 7 | `Eagle` | `animals/eagle.py` | Concrete (leaf) | `Bird` |
| 8 | `Parrot` | `animals/parrot.py` | Concrete (leaf) | `Bird` |
| 9 | `Crocodile` | `animals/crocodile.py` | Concrete (leaf) | `Reptile` |
| 10 | `Gecko` | `animals/gecko.py` | Concrete (leaf) | `Reptile` |
| 11 | `Habitat` | `habitat.py` | Standalone | `object` (no custom parent) |
| 12 | `Finance` | `finance.py` | Singleton | `object` |
| 13 | `Zoo` | `zoo.py` | Orchestrator | `object` |

---

## 4. Inheritance Hierarchy

```
object  (Python built-in)
│
├── ABC  (abc module)
│    │
│    └── Animal                  ← abstract base class
│         │
│         ├── Mammal             ← intermediate; adds fur_colour, is_warm_blooded=True
│         │    ├── Lion          ← concrete; adds mane_length, hunt()
│         │    └── Elephant      ← concrete; adds tusk_length_cm, spray_water()
│         │
│         ├── Bird               ← intermediate; adds wingspan_cm, can_fly
│         │    ├── Eagle         ← concrete; adds altitude_m, dive()
│         │    └── Parrot        ← concrete; adds vocabulary, talk(), learn_word()
│         │
│         └── Reptile            ← intermediate; adds scale_colour, is_warm_blooded=False
│              ├── Crocodile     ← concrete; adds length_m, death_roll()
│              └── Gecko         ← concrete; adds can_regrow_tail, climb_wall()
│
├── Habitat                      ← no custom parent; manages animal rosters + environment
│
├── Finance                      ← Singleton; one instance tracks all money
│
└── Zoo                          ← Orchestrator; owns Habitats, uses Finance
```

**Depth of deepest chain:** 4 levels  
`object → ABC → Animal → Mammal/Bird/Reptile → Lion/Elephant/Eagle/Parrot/Crocodile/Gecko`

---

## 5. Class-by-Class Deep Dive

### 5.1 `Animal` (ABC – Abstract Base Class)

**File:** `ozzoo/animals/animal.py`  
**Inherits from:** `ABC` (Python's `abc.ABC`)  
**Cannot be instantiated directly.**

#### Purpose
Defines the common interface and shared behaviour for every zoo animal.  
Because it inherits from `ABC` and marks two methods with `@abstractmethod`, any concrete subclass **must** implement them or Python will raise a `TypeError`.

#### Private attributes (encapsulation)
Python's double-underscore name-mangling is used so these attributes cannot be  
accidentally read or written from outside the class:

| Private attribute | Type | Range | Accessed via property |
|-------------------|------|-------|----------------------|
| `__name` | `str` | — | `name` (read-only) |
| `__species` | `str` | — | `species` (read-only) |
| `__health` | `int` | 0–100 | `health` / `health.setter` |
| `__hunger` | `int` | 0–100 | `hunger` / `hunger.setter` |
| `__happiness` | `int` | 0–100 | `happiness` / `happiness.setter` |

All setters clamp values to the valid range using `max(0, min(100, value))`.

#### Class variable and public accessor
```python
_ticket_price: float = 10.0   # default admission price; overridden by subclasses
```
A public read-only `ticket_price` property exposes this value without requiring direct
access to the protected `_ticket_price` attribute.

#### Abstract methods (must be overridden)
| Method | Returns | Description |
|--------|---------|-------------|
| `sound()` | `str` | Characteristic sound of the animal |
| `diet()` | `str` | Diet type ('carnivore', 'herbivore', …) |

#### Concrete methods (shared by all animals)
| Method | Effect |
|--------|--------|
| `feed(amount=20)` | Decreases hunger, slightly increases happiness |
| `play(duration_minutes=15)` | Increases happiness and hunger |
| `receive_treatment(points=20)` | Restores health |
| `status()` | Returns a formatted status string |

---

### 5.2 `Mammal`

**File:** `ozzoo/animals/mammal.py`  
**Inherits from:** `Animal`  
**Inheritance chain:** `Mammal → Animal → ABC → object`

#### Purpose
Intermediate class for all warm-blooded, fur-bearing animals.  
Provides default implementations of `sound()` and `diet()` (both overridden by concrete subclasses) and adds a new behaviour: `groom()`.

#### Added attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `fur_colour` | `str` | Coat colour (e.g., "golden", "grey") |
| `is_warm_blooded` | `bool` | Class constant = `True` |

#### New methods
| Method | Effect |
|--------|--------|
| `groom()` | Grooming session; boosts happiness +10 |

---

### 5.3 `Bird`

**File:** `ozzoo/animals/bird.py`  
**Inherits from:** `Animal`  
**Inheritance chain:** `Bird → Animal → ABC → object`

#### Purpose
Intermediate class for feathered, egg-laying vertebrates.

#### Added attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `wingspan_cm` | `float` | Wingspan in centimetres |
| `can_fly` | `bool` | Whether the bird is flight-capable |
| `is_warm_blooded` | `bool` | Class constant = `True` |

#### New methods
| Method | Effect |
|--------|--------|
| `fly()` | If `can_fly`, boosts happiness +15; otherwise returns an error message |

---

### 5.4 `Reptile`

**File:** `ozzoo/animals/reptile.py`  
**Inherits from:** `Animal`  
**Inheritance chain:** `Reptile → Animal → ABC → object`

#### Purpose
Intermediate class for cold-blooded, scaly vertebrates.

#### Added attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `scale_colour` | `str` | Dominant scale colour |
| `is_venomous` | `bool` | True if the animal produces venom |
| `is_warm_blooded` | `bool` | Class constant = `False` |

#### New methods
| Method | Effect |
|--------|--------|
| `bask(minutes=30)` | Cold-blooded basking in the sun; restores health |

---

### 5.5 `Lion`

**File:** `ozzoo/animals/lion.py`  
**Inherits from:** `Mammal`  
**Inheritance chain:** `Lion → Mammal → Animal → ABC → object`

#### Overrides / additions
| Item | Value / Behaviour |
|------|-------------------|
| `species` | `"Panthera leo"` (set automatically) |
| `fur_colour` | `"golden"` (set automatically) |
| `_ticket_price` | `$25.00` |
| `sound()` | `"ROAR"` |
| `diet()` | `"carnivore"` |
| `mane_length` | `str` – `"short"` / `"medium"` / `"long"` |
| `is_male` | `bool` |
| `hunt()` | Drains energy (+20 hunger), boosts happiness (+10) |

---

### 5.6 `Elephant`

**File:** `ozzoo/animals/elephant.py`  
**Inherits from:** `Mammal`  
**Inheritance chain:** `Elephant → Mammal → Animal → ABC → object`

| Item | Value / Behaviour |
|------|-------------------|
| `species` | `"Loxodonta africana"` |
| `fur_colour` | `"grey"` |
| `_ticket_price` | `$20.00` |
| `sound()` | `"TRUMPET"` |
| `diet()` | `"herbivore"` |
| `tusk_length_cm` | `float` |
| `spray_water()` | Restores health (+5) and boosts happiness (+8) |

---

### 5.7 `Eagle`

**File:** `ozzoo/animals/eagle.py`  
**Inherits from:** `Bird`  
**Inheritance chain:** `Eagle → Bird → Animal → ABC → object`

| Item | Value / Behaviour |
|------|-------------------|
| `species` | `"Haliaeetus leucocephalus"` |
| `wingspan_cm` | `210.0` cm (set automatically) |
| `_ticket_price` | `$18.00` |
| `sound()` | `"SCREECH"` |
| `diet()` | `"carnivore"` |
| `altitude_m` | `int` – typical soaring altitude |
| `dive()` | Reduces hunger (−15), boosts happiness (+12) |

---

### 5.8 `Parrot`

**File:** `ozzoo/animals/parrot.py`  
**Inherits from:** `Bird`  
**Inheritance chain:** `Parrot → Bird → Animal → ABC → object`

| Item | Value / Behaviour |
|------|-------------------|
| `species` | `"Ara macao"` |
| `wingspan_cm` | `100.0` cm |
| `_ticket_price` | `$12.00` |
| `sound()` | `"SQUAWK"` |
| `diet()` | `"herbivore"` |
| `vocabulary` | `list[str]` – words the parrot knows |
| `talk()` | Picks a random word from vocabulary, boosts happiness +5 |
| `learn_word(word)` | Adds a new word to vocabulary |

---

### 5.9 `Crocodile`

**File:** `ozzoo/animals/crocodile.py`  
**Inherits from:** `Reptile`  
**Inheritance chain:** `Crocodile → Reptile → Animal → ABC → object`

| Item | Value / Behaviour |
|------|-------------------|
| `species` | `"Crocodylus niloticus"` |
| `scale_colour` | `"dark green"` |
| `is_venomous` | `False` |
| `_ticket_price` | `$15.00` |
| `sound()` | `"HISS-SNAP"` |
| `diet()` | `"carnivore"` |
| `length_m` | `float` – body length |
| `death_roll()` | Increases hunger (+15), big happiness boost (+20) |

---

### 5.10 `Gecko`

**File:** `ozzoo/animals/gecko.py`  
**Inherits from:** `Reptile`  
**Inheritance chain:** `Gecko → Reptile → Animal → ABC → object`

| Item | Value / Behaviour |
|------|-------------------|
| `species` | `"Eublepharis macularius"` |
| `scale_colour` | `"yellow-spotted"` |
| `is_venomous` | `False` |
| `_ticket_price` | `$8.00` |
| `sound()` | `"chirp-chirp"` |
| `diet()` | `"insectivore"` |
| `can_regrow_tail` | `True` (class constant) |
| `climb_wall()` | Adhesive toe-pad climbing; boosts happiness +10 |

---

### 5.11 `Habitat`

**File:** `ozzoo/habitat.py`  
**Inherits from:** `object` (no custom parent)

#### Purpose
Models a single physical enclosure inside the zoo.  
Every animal must be placed into a `Habitat` before it can interact with the simulation.

#### Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Display name (e.g., "African Savannah") |
| `climate` | `str` | One of: `tropical`, `arid`, `temperate`, `aquatic`, `arctic` |
| `enclosure_type` | `str` | One of: `open`, `cage`, `tank`, `aviary`, `terrarium` |
| `capacity` | `int` | Max number of animals allowed |
| `area_sqm` | `float` | Floor area in square metres |
| `_animals` | `list[Animal]` | Animals currently residing here (private) |

#### Class constants
```python
VALID_CLIMATES   = ("tropical", "arid", "temperate", "aquatic", "arctic")
VALID_ENCLOSURES = ("open", "cage", "tank", "aviary", "terrarium")
```
If an invalid climate or enclosure type is passed to `__init__`, a `ValueError` is raised immediately.

#### Properties
| Property | Description |
|----------|-------------|
| `occupancy` | Current animal count (read-only) |
| `animals` | Read-only copy of the internal animal list |

#### Methods
| Method | Description |
|--------|-------------|
| `add_animal(animal)` | Adds an animal if capacity allows |
| `remove_animal(animal)` | Removes an animal by reference |
| `simulate_day()` | Advances the habitat by one day (see below) |
| `report()` | Formatted multi-line status string |

---

### 5.12 `Finance` (Singleton)

**File:** `ozzoo/finance.py`  
**Inherits from:** `object`  
**Design pattern:** Singleton

#### Purpose
Ensures that only **one** financial ledger exists for the entire zoo.

#### Singleton mechanism
```python
class Finance:
    _instance: Finance | None = None   # class-level reference
    _initialised: bool = False         # guard to prevent double-init

    def __new__(cls) -> Finance:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance            # always returns the same object

    def __init__(self) -> None:
        if self._initialised:
            return                      # skip if already set up
        # … initialise attributes only once
        self._initialised = True
```

Calling `Finance()` ten times returns the **same object** every time.

#### Private attributes (properties)
| Attribute | Type | Description |
|-----------|------|-------------|
| `__balance` | `float` | Current cash balance (starts at $50,000) |
| `__revenue` | `float` | Cumulative income |
| `__expenses` | `float` | Cumulative expenditure |

#### Methods
| Method | Description |
|--------|-------------|
| `charge_admission(price, count)` | Records ticket sales |
| `pay_food_bill(amount)` | Deducts food costs |
| `pay_vet_bill(amount)` | Deducts vet costs |
| `record_expense(description, amount)` | Generic debit |
| `record_income(description, amount)` | Generic credit |
| `report()` | Formatted financial summary |
| `reset()` *(class method)* | Destroys singleton — **tests only** |

---

### 5.13 `Zoo`

**File:** `ozzoo/zoo.py`  
**Inherits from:** `object`

#### Purpose
Top-level orchestrator.  Uses **composition** (has-a) rather than inheritance:
- `Zoo` **has** `Finance` (singleton, referenced in `_finance`)
- `Zoo` **has** `list[Habitat]` (stored in `_habitats`)

#### Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Zoo display name |
| `location` | `str` | Geographic location |
| `_habitats` | `list[Habitat]` | All habitats managed by this zoo |
| `_finance` | `Finance` | The singleton financial ledger |

#### Methods
| Method | Description |
|--------|-------------|
| `add_habitat(habitat)` | Registers a new habitat |
| `remove_habitat(habitat)` | Unregisters a habitat |
| `get_habitat(name)` | Finds a habitat by name |
| `place_animal(animal, habitat_name)` | Delegates to `Habitat.add_animal()` |
| `admit_visitors(count)` | Iterates animals; charges admission via `Finance` |
| `simulate_day()` | Calls `Habitat.simulate_day()` for each habitat; deducts operating costs |
| `full_report()` | Aggregates habitat reports + finance report |

---

## 6. Habitat – Everything You Need to Know

A `Habitat` is the **physical space** where animals live inside the zoo.  
It is one of the most important classes because it:

1. **Controls access** – `add_animal()` enforces the capacity limit and returns a clear message if full.
2. **Validates environment** – invalid climate or enclosure type raises a `ValueError` at creation time.
3. **Drives daily simulation** – `simulate_day()` contains the core game-loop logic:

```
For each animal in the habitat:
  ├── Increase hunger by +5 (animals get hungry every day)
  │
  ├── If animal is a Reptile AND climate is 'arid' or 'tropical':
  │       Automatically increase health by +3  (warm climate helps reptiles)
  │
  └── If climate is 'aquatic':
          Automatically increase happiness by +5  (animals love the water)
```

### Climate types and their effects

| Climate | Automatic daily bonus |
|---------|----------------------|
| `arid` | Reptiles auto-bask: +3 health |
| `tropical` | Reptiles auto-bask: +3 health |
| `aquatic` | All animals: +5 happiness |
| `temperate` | No automatic bonus |
| `arctic` | No automatic bonus |

### Enclosure types (informational only)

| Enclosure | Typical use |
|-----------|------------|
| `open` | Large mammals on an open plain (lions, elephants) |
| `cage` | Animals that need barriers for safety |
| `tank` | Aquatic or semi-aquatic animals |
| `aviary` | Birds – large netted spaces for flight |
| `terrarium` | Small reptiles and amphibians |

### Example habitats in the demo

| Habitat | Climate | Enclosure | Residents |
|---------|---------|-----------|-----------|
| African Savannah | arid | open | Simba (Lion), Nala (Lion), Dumbo (Elephant) |
| Sky Aviary | tropical | aviary | Freedom (Eagle), Polly (Parrot) |
| Reptile House | tropical | terrarium | Snappy (Crocodile), Leo (Gecko) |

Because the Reptile House has a **tropical** climate, Snappy and Leo automatically  
bask every simulated day and gain +3 health without any manual intervention.

---

## 7. OOP Concepts Used

| Concept | Where |
|---------|-------|
| **Abstraction** | `Animal` is an ABC; `sound()` and `diet()` are abstract — subclasses must implement them |
| **Encapsulation** | `Animal`, `Finance` use `__attr` (double underscore) with `@property` + setter |
| **Inheritance** | Full 4-level chain: `Animal → Mammal/Bird/Reptile → concrete species` |
| **Polymorphism** | `lion.sound()` → `"ROAR"`, `parrot.sound()` → `"SQUAWK"` — same method name, different result |
| **Composition** | `Zoo` *has* `Finance` and `Habitat` objects (uses them without inheriting from them) |
| **Singleton** | `Finance` — only one ledger can exist; `__new__` + `_initialised` guard |
| **Class variables** | `_ticket_price`, `is_warm_blooded`, `can_regrow_tail` — shared across all instances of a class |
| **`super()`** | Every subclass calls `super().__init__()` to ensure the parent chain is properly initialised |
| **Type hints** | All methods and attributes carry Python type annotations for clarity |
| **`@abstractmethod`** | Prevents `Animal` from being instantiated directly |

---

## 8. Running the Program

```bash
# From the repository root:
python -m ozzoo.main

# Or directly:
python ozzoo/main.py
```

Expected output includes habitat reports, animal interactions, visitor admission logs, daily simulation events, and a full financial summary.
