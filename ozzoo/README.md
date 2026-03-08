# OzZoo — Australian Zoo Simulation Game 🦘

## Project Overview

**OzZoo** is a complete, production-quality Python Zoo Simulation Game built as a university
Object-Oriented Programming assignment.  It models an Australian zoo with real animal species,
enclosures, habitats, visitors, finances, and daily simulation events.

> *"Step into the shoes of an Australian zoo manager — feed your kangaroos, treat your sick
> koalas, manage your budget, and keep visitors happy!"*

---

## Background Story

OzZoo was established in the heart of the Australian outback.  Starting with a handful of
iconic native animals — two Red Kangaroos, two Koalas, two Little Penguins, a Saltwater
Crocodile, and a Wedge-tailed Eagle — your mission is to grow OzZoo into the most celebrated
zoo in Australia.

Each day brings new challenges: animals grow hungry, enclosures get dirty, funds dwindle, and
random events (heatwaves, disease outbreaks, generous donors) keep you on your toes.

---

## Setup Instructions

### Requirements

- **Python** 3.10 or higher (uses `match` statement syntax indirectly via type hints)
- No third-party dependencies — the entire project uses the Python standard library.
- **GUI only:** `tkinter` (included with the standard Python installer on Windows and macOS;
  on Debian/Ubuntu run `sudo apt-get install python3-tk`)

### Installation

```bash
# Clone the repository
git clone https://github.com/MananSharma001/MananSharma001.git
cd MananSharma001/ozzoo

# Run the game (CLI)
python main.py

# Run the game (GUI)
python main.py --gui
```

---

## How to Run

### Terminal / Command Prompt

```bash
cd ozzoo

# CLI mode (text menus)
python main.py

# GUI mode (tkinter window)
python main.py --gui
```

### Graphical Interface (GUI)

OzZoo ships with a full **tkinter GUI** that you can launch with:

```bash
python main.py --gui
```

The GUI provides:

| Tab | What you can do |
|---|---|
| 🐾 **Animals** | View all animals (health colour-coded), feed, medicate, buy, move to enclosure, make perform |
| 🏠 **Enclosures** | View cleanliness (colour-coded), clean, upgrade, build new enclosure |
| 🛒 **Resources** | View food & medicine stock, buy food, buy medicine |
| 💰 **Finances** | Full financial report, set ticket price, view income / expense breakdown |
| 📋 **Event Log** | See all zoo events from the current session |

**Footer controls (always visible):**

- **Advance Day ➜** — simulate one full day (visitors arrive, animals tick, random events fire); a popup shows the daily report
- **Save Game** — save to `ozzoo_save.json`
- **Load Game** — restore from `ozzoo_save.json`
- **Quit** — exit with confirmation

### Running in VS Code

> **TL;DR** — open the repo folder in VS Code, install the Python extension, then press **F5**.

Three launch configurations are provided in `.vscode/launch.json`:

| Config name | What it does |
|---|---|
| **Run OzZoo (CLI)** | Opens the text-menu game in the integrated terminal |
| **Run OzZoo (GUI)** | Opens the tkinter GUI window |
| **Run OzZoo (CLI + debugger)** | CLI with full debugger support |

#### Step-by-step

1. **Install VS Code** — download from <https://code.visualstudio.com/> if you haven't already.

2. **Open the project folder** in VS Code:

   ```
   File → Open Folder → select the repository root folder
   ```

   *(The folder that contains `ozzoo/` and `.vscode/`.)*

3. **Install the Python extension** — VS Code will show a pop-up:
   *"Do you want to install the recommended extensions?"* → click **Install**.
   If the pop-up doesn't appear, press `Ctrl+Shift+X`, search for **Python** (by Microsoft) and install it.

4. **Select a Python interpreter** — press `Ctrl+Shift+P`, type
   `Python: Select Interpreter`, and choose **Python 3.10** or higher.

5. **Run the game** — press `Ctrl+Shift+D` to open the *Run and Debug* panel, choose
   **"Run OzZoo (GUI)"** from the dropdown, then press **F5**.

#### Manual terminal inside VS Code

```bash
# CLI
python main.py

# GUI
python main.py --gui
```

#### Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Make sure VS Code opened the **repository root** folder (the one that contains `ozzoo/` and `.vscode/`), not the `ozzoo` sub-folder directly. |
| `python: command not found` | Use `python3 main.py` instead, or set `"python.defaultInterpreterPath"` in `.vscode/settings.json`. |
| `No module named 'tkinter'` | Install tkinter: `sudo apt-get install python3-tk` (Linux) or reinstall Python with the standard installer (Windows/macOS). |
| Input not working in Debug Console | The CLI uses stdin — always run with **F5** in the integrated terminal config. |
| `SyntaxError` / wrong Python version | OzZoo requires **Python 3.10+**. Check your version with `python --version`. |

---

## How to Play (User Guide)

When the game starts you are presented with the **Main Menu**:

```
=== OzZoo Management System ===
Day: X | Funds: $X | Visitors Today: X

[1]  View Zoo Status
[2]  Manage Animals
[3]  Manage Enclosures
[4]  Manage Resources
[5]  Manage Finances
[6]  Advance Day  ➜
[7]  View Event Log
[8]  Save Game
[9]  Load Game
[0]  Quit
```

### Daily Gameplay Loop

1. **Advance Day [6]** — press 6 to simulate one day.  Animals get hungrier, visitors arrive,
   finances update, and random events may fire.
2. **Feed your animals [2c]** — if animals are hungry (hunger > 20) you *must* feed them or
   their health will drop.
3. **Clean enclosures [3c]** — dirty enclosures make animals unhappy.
4. **Monitor finances [5]** — ticket revenue comes in every day, but food, medicine, and
   upkeep cost money.
5. **Buy more animals [2b]** — use the Factory to purchase new species and grow your zoo.
6. **Save regularly [8]** — save to `ozzoo_save.json` and reload anytime.

### Tips

- Keep animal **health > 30** to avoid welfare alerts.
- Keep animal **happiness > 60** to attract more visitors (more revenue).
- Two healthy, happy animals of the same species in the same enclosure have a **10 % chance**
  of producing a baby each day.
- Random events (heatwave, disease, donations) occur with a **25 % daily probability**.

---

## UML Class Diagram (ASCII)

```
Animal (ABC)
│
├── Mammal (ABC)
│   └── Marsupial (ABC)
│       ├── Kangaroo  ← make_sound(), eat(), sleep(), jump(), box()
│       └── Koala     ← make_sound(), eat(), sleep(), climb()
│
├── Bird (ABC)
│   ├── Eagle         ← make_sound(), eat(), sleep(), soar()
│   └── FlightlessBird (ABC)
│       ├── Penguin   ← make_sound(), eat(), swim(), waddle()
│       └── Emu       ← make_sound(), eat(), run()
│
└── Reptile (ABC)
    ├── Crocodile     ← make_sound(), eat(), snap()
    └── Snake         ← make_sound(), eat(), slither()

ICleanable (interface)
├── Enclosure         ← clean(), daily_tick(), add_animal(), ...
└── Habitat           ← clean(), daily_tick(), add_enclosure(), ...

Finance (Singleton)   ← add_income(), deduct_expense(), get_report()
FoodInventory         ← purchase(), consume(), report()
MedicineInventory     ← purchase(), administer(), report()
Visitor               ← visit_enclosure(), leave_donation()

ZooEventManager       ← subscribe(), notify()
  ├── WelfareObserver
  ├── FinanceObserver
  └── EventLogger

AnimalFactory         ← create_animal(species_type, name, age)

Zoo                   ← advance_day(), feed_animal(), buy_animal(), ...
GameLoop              ← tick()
CLI                   ← run()
```

---

## Design Patterns Used

### 1. Observer Pattern (`patterns/observer.py`)

**Why?**  The zoo needs to react to events (low health, low funds) without tight coupling
between the animal/finance code and the notification/logging code.

- `ZooEventManager` — subject that manages subscriptions
- `WelfareObserver` — prints a welfare alert when animal health < 30
- `FinanceObserver` — warns when balance < $1,000
- `EventLogger` — logs every event with a timestamp

### 2. Factory Pattern (`patterns/factory.py`)

**Why?**  Creating animals should be centralised.  New species can be added to the registry
without changing any other code.

- `AnimalFactory.create_animal("kangaroo", "Joey")` — returns a fully initialised `Kangaroo`

### 3. Singleton Pattern (`finance.py`)

**Why?**  There must be *exactly one* financial record for the entire zoo.  Every module that
needs money uses `Finance.get_instance()`.

---

## Class Descriptions

| Class | Description |
|---|---|
| `Animal` | Abstract base class — defines the contract for all zoo animals |
| `Mammal` | Abstract mammal with fur-colour attribute |
| `Bird` | Abstract bird with wingspan and flight capability |
| `Reptile` | Abstract reptile with scale colour and venom flag |
| `Marsupial` | Abstract pouched mammal — adds joey state |
| `FlightlessBird` | Abstract non-flying bird — adds speed attribute |
| `Kangaroo` | Concrete marsupial — jump(), box() |
| `Koala` | Concrete marsupial — climb(), champion sleeper |
| `Penguin` | Concrete flightless bird — swim(), waddle() |
| `Emu` | Concrete flightless bird — run() |
| `Crocodile` | Concrete reptile — snap() |
| `Snake` | Concrete reptile — slither(), venomous |
| `Eagle` | Concrete bird — soar() |
| `Enclosure` | Physical housing unit with cleanliness and capacity |
| `Habitat` | Geographic zone grouping multiple enclosures |
| `Visitor` | Zoo guest with satisfaction tracking |
| `FoodInventory` | Manages all food stock |
| `MedicineInventory` | Manages all medicine stock |
| `Finance` | Singleton financial manager |
| `Zoo` | Top-level coordinator |
| `GameLoop` | Wraps day-advancement with formatted output |
| `CLI` | Interactive command-line interface |
| `AnimalFactory` | Factory for creating animal instances |
| `ZooEventManager` | Observer event publisher |
| `WelfareObserver` | Animal health alert observer |
| `FinanceObserver` | Low-funds alert observer |
| `EventLogger` | Event log observer |
| `ICleanable` | Interface for cleanable zoo structures |

---

## AI Copilot Usage

*[Placeholder — replace with actual AI usage log]*

| Task | Tool Used | Prompt Summary | Changes Made |
|---|---|---|---|
| Project scaffolding | GitHub Copilot | "Create OzZoo structure" | Created all files |
| Observer pattern | GitHub Copilot | "Implement Observer" | observer.py |
| Type hints | GitHub Copilot | "Add type hints" | All files |

---

*OzZoo — Built with 🐍 Python and ❤️ for Australian wildlife.*
