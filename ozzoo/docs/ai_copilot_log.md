# OzZoo — AI Copilot Usage Log

This log documents significant interactions with GitHub Copilot during the development of the OzZoo zoo management simulation.  Each entry shows the prompt intent, what was generated, and a critical analysis of the output.

---

## Entry 1 — Initial Architecture Design

**Date:** Development Phase 1  
**Tool:** GitHub Copilot (Chat)  
**Files affected:** `zoo.py`, `animals/animal.py`, `finance.py`

### Prompt

> "Design a Python zoo simulation with OOP principles — at least 10 classes, 4-level inheritance
> hierarchy, ABC abstractions, and three design patterns: Singleton, Factory, Observer."

### AI Output (Snippet)

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    def __init__(self, name: str, species: str, age: int):
        self.__health    = 100
        self.__hunger    = 0
        self.__happiness = 80

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def eat(self, amount: int = 1) -> str: ...
```

### Analysis

- ✅ **Accepted as-is:** The ABC structure, double-underscore name mangling, and abstract method
  signatures were exactly right.
- ✅ **Accepted:** The `@property` + clamped setter pattern for `health`, `hunger`, `happiness`.
- ❌ **Rejected:** Copilot initially put all animal classes in one file (`animals.py`).  I
  restructured this into a package (`animals/animal.py`, `animals/mammal.py`, etc.) for
  cohesion and the four-level depth requirement.
- **Learned:** AI tends to put everything in one file for brevity; hierarchical package structure
  must be enforced manually.

---

## Entry 2 — Singleton Finance Class

**Date:** Development Phase 1  
**Tool:** GitHub Copilot (inline)  
**Files affected:** `finance.py`

### Prompt

> "Implement a Finance class as a Singleton in Python using `__new__` override with an
> `_initialised` guard so that `reset()` can destroy the singleton for testing."

### AI Output (Snippet)

```python
class Finance:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return
        self.__balance = 10_000.0
        self._initialised = True

    @classmethod
    def reset(cls):
        cls._instance = None
```

### Analysis

- ✅ **Accepted completely:** This is the canonical Python Singleton with reset support.
- ⚠️ **Added:** Type hints, docstrings, `_income_ledger` / `_expense_ledger` for full financial
  tracking, `get_report()` method, and `get_recent_ledger()` for the GUI ledger treeview.
- **Learned:** Copilot generates correct structural code but rarely adds comprehensive
  application-specific attributes on the first pass.

---

## Entry 3 — Observer Pattern for Welfare Alerts

**Date:** Development Phase 2  
**Tool:** GitHub Copilot (Chat)  
**Files affected:** `patterns/observer.py`

### Prompt

> "Implement the Observer pattern in Python.  Create an abstract Observer base class with
> `update(event_type, data)`, a ZooEventManager publisher that allows subscribe/unsubscribe,
> and three concrete observers: WelfareObserver, FinanceObserver, and EventLogger."

### AI Output (Snippet)

```python
class ZooEventManager:
    def __init__(self):
        self._listeners: dict[str, list[Observer]] = {}

    def subscribe(self, event_type: str, observer: Observer) -> None:
        self._listeners.setdefault(event_type, []).append(observer)

    def notify(self, event_type: str, data: dict) -> None:
        for obs in self._listeners.get(event_type, []):
            obs.update(event_type, data)
```

### Analysis

- ✅ **Accepted:** The core subscribe/notify structure was correct.
- ❌ **Rejected:** Copilot added `unsubscribe()` but used linear list removal which is O(n).
  I kept this since the observer count is small.
- ⚠️ **Modified:** Added `get_all_entries()` to `EventLogger` to expose the log list to the GUI
  without breaking encapsulation (returning a copy instead of `self._log`).
- **Learned:** Copilot correctly implements the GoF Observer but doesn't anticipate GUI
  integration needs (such as clearing the log after display).

---

## Entry 4 — Factory Pattern with Lazy Imports

**Date:** Development Phase 2  
**Tool:** GitHub Copilot (inline)  
**Files affected:** `patterns/factory.py`

### Prompt

> "Create an AnimalFactory that uses a registry dict mapping species name to (module_path,
> class_name) tuples.  Use importlib.import_module to avoid circular imports."

### AI Output (Snippet)

```python
class AnimalFactory:
    _REGISTRY = {
        "kangaroo": ("animals.marsupial", "Kangaroo"),
        "penguin":  ("animals.flightless_bird", "Penguin"),
    }

    @classmethod
    def create_animal(cls, species: str, name: str, **kwargs) -> Animal:
        module_path, class_name = cls._REGISTRY[species.lower()]
        module = importlib.import_module(module_path)
        cls_obj = getattr(module, class_name)
        return cls_obj(name, **kwargs)
```

### Analysis

- ✅ **Accepted:** The registry pattern and importlib approach are exactly right.
- ⚠️ **Modified:** Added all 7 species to the registry and added `get_available_species()`
  and `get_price(species)` methods for the GUI buy dialog.
- ❌ **Rejected:** Copilot used `**kwargs` everywhere which hides intent.  Changed to explicit
  `age: int = 1` parameter.
- **Learned:** `importlib.import_module` is the correct solution for circular import avoidance;
  Copilot knows this pattern well.

---

## Entry 5 — tkinter Dark-Theme GUI

**Date:** Development Phase 3  
**Tool:** GitHub Copilot (Chat)  
**Files affected:** `gui.py`

### Prompt

> "Create a dark-themed tkinter GUI with a ttk.Notebook containing 6 tabs (Dashboard, Animals,
> Enclosures, Resources, Finances, Event Log).  Use canvas-based progress bars for welfare
> metrics.  No third-party dependencies."

### AI Output (Snippet)

```python
class _CanvasBar(tk.Canvas):
    HEIGHT = 16
    RADIUS = 6

    def update_bar(self, value: int, colour: str = "#43a047") -> None:
        self.delete("all")
        w = self.winfo_width()
        filled = int(w * value / 100)
        # Draw background
        self.create_rectangle(0, 0, w, self.HEIGHT, fill="#2a2a4a", outline="")
        # Draw filled portion
        if filled > 0:
            self.create_rectangle(0, 0, filled, self.HEIGHT, fill=colour, outline="")
```

### Analysis

- ✅ **Accepted:** The canvas-based bar widget is cleaner than `ttk.Progressbar` for custom colours.
- ❌ **Rejected:** Copilot's initial layout used `grid()` inconsistently.  Replaced with
  `pack()` throughout for simpler responsive layout.
- ⚠️ **Heavily modified:** Added KPI tile widgets, detail panels with individual animal bars,
  enclosure cleanliness/occupancy bars, scrollable ledger treeview, and colour-tagged event log.
- **Learned:** Copilot can scaffold GUI structure well but complex interactive details (selection
  → detail panel updates, sorted treeviews, colour-coded tags) require manual implementation.

---

## Entry 6 — Achievement System

**Date:** Development Phase 4  
**Tool:** GitHub Copilot (Chat)  
**Files affected:** `achievements.py`

### Prompt

> "Design an achievement system for a zoo game.  Each achievement has a key, title, description,
> icon, check function (zoo, stats) -> bool, and optional cash reward.  The tracker should
> never re-fire the same achievement twice and must be serialisable to JSON."

### AI Output

Copilot generated the `@dataclass Achievement` and the tracker skeleton correctly.

### Analysis

- ✅ **Accepted:** Dataclass structure, `_unlocked: set[str]`, `check_all()` returning newly
  unlocked list.
- ⚠️ **Modified:** Expanded from 5 placeholder achievements to 24 full achievements across
  7 categories.  Added `to_dict()` / `from_dict()` for persistence.
- ❌ **Rejected:** Copilot used `except Exception: pass` which is too broad.  Changed to
  `except (AttributeError, KeyError, TypeError, ZeroDivisionError)` for targeted suppression.
- **Learned:** AI generates correct structure but domain-specific content (the actual
  24 achievements) must be crafted by the developer.

---

## Entry 7 — Animated Toast Notifications

**Date:** Development Phase 4  
**Tool:** GitHub Copilot (Chat)  
**Files affected:** `gui.py`

### Prompt

> "Create a tkinter toast notification that slides in from the right side of the window,
> stays visible for 3.5 seconds, then slides back out.  Non-blocking.  Use after() for animation."

### AI Output (Snippet)

```python
class Toast:
    @classmethod
    def show(cls, root, message, colour="#f9a825"):
        win = tk.Toplevel(root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        # Position and animate...
        root.after(3500, win.destroy)
```

### Analysis

- ✅ **Accepted:** `overrideredirect(True)` + `attributes("-topmost")` is correct for borderless
  floating notifications.
- ❌ **Rejected:** Copilot's animation was abrupt (no slide-in).  I implemented a proper
  `_slide(step)` recursive `after()` animation over 12 frames.
- ⚠️ **Modified:** Added slide-out animation, configurable `bg`/`colour`, and proper cleanup
  if the root window is destroyed while the toast is open (`winfo_exists()` check).
- **Learned:** Copilot knows tkinter patterns well but smooth animation requires manual iterative
  refinement to get the timing/frame count right.

---

## Entry 8 — Comprehensive Test Suite

**Date:** Development Phase 5  
**Tool:** GitHub Copilot (Chat)  
**Files affected:** `tests/test_oop_requirements.py`

### Prompt

> "Write a 100-test unittest suite covering all 12 OOP assignment requirements: encapsulation
> (name mangling), inheritance depth, ABC enforcement, Singleton/Factory/Observer patterns,
> custom exceptions, game loop, finance, food inventory, animal welfare, achievements, and
> challenges."

### AI Output

Copilot generated the overall test class structure and most test method stubs.

### Analysis

- ✅ **Accepted:** Test class organisation by requirement, use of `setUp()` for Finance.reset(),
  `assertRaises()` for exception tests.
- ❌ **Rejected / Fixed:** Copilot used wrong argument names (`capacity=` instead of
  `max_capacity=`, `heal()` instead of `apply_medicine()`) — required checking actual API.
- ❌ **Rejected:** Assumed Finance starts at balance $0; actual starting balance is `STARTING_BALANCE = $10,000`.
- **Learned:** AI-generated tests are a great starting point but always need to be run against
  the real codebase.  16 of 100 tests needed fixes due to API mismatches — a 16% manual
  correction rate.

---

## Summary Statistics

| Metric | Value |
|---|---|
| Total significant AI interactions | 8 |
| Files where AI output was accepted verbatim | 1 (`finance.py` core structure) |
| Files heavily modified from AI output | 4 (`gui.py`, `achievements.py`, `zoo.py`, tests) |
| Files where AI output was mostly rejected | 0 |
| Average acceptance rate of AI suggestions | ~70% |
| Test correction rate (API mismatches) | 16% |

### Key Lessons

1. **AI excels at:** structural patterns (Singleton, Factory, Observer), type hints, docstring templates, boilerplate widget creation.
2. **AI struggles with:** application-specific content (actual achievement descriptions, game balance), API precision (wrong argument names), complex animation logic.
3. **Best practice:** Use AI to scaffold structure, then manually refine content, verify APIs, and add domain knowledge.
4. **Always run tests:** AI-generated tests are valuable but always contain API mismatches that only surface when run against the real code.
