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
| 📊 **Dashboard** | Live KPI tiles (Balance, Day, Animals, Score) + canvas welfare meters + zoo statistics |
| 🐾 **Animals** | Sortable treeview; select a row for individual stat bars; feed, medicate, buy, move, make perform |
| 🏠 **Enclosures** | Cleanliness & occupancy bars; clean, upgrade, build new enclosure |
| 🛒 **Resources** | Canvas progress bars per food/medicine type; inline buy buttons |
| 💰 **Finances** | KPI tiles (balance, income, expenses, ticket price) + scrollable transaction ledger |
| 📋 **Event Log** | Colour-coded daily reports (Birth / Death / Welfare / Finance / Random / Habitat) |

**Footer controls (always visible):**

- **⏩ Advance Day** — simulate one full day; a popup shows the colour-coded daily report
- **💾 Save** — save to `ozzoo_save.json`
- **📂 Load** — restore from `ozzoo_save.json`
- **❓ How to Play** — opens the in-game help guide with 9 detailed sections
- **Quit** — exit with confirmation and final score

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

## How to Play — Complete Guide

> **In-game shortcut:** Click the **❓ How to Play** button in the GUI footer at any time to open
> the interactive help dialog with the same information below, searchable by section.

### 🎮 Overview

You are the manager of **OzZoo**, an Australian wildlife zoo.  Your zoo starts on **Day 0** with:

- **8 animals** — 2 Red Kangaroos, 2 Koalas, 2 Little Penguins, 1 Saltwater Crocodile, 1 Wedge-tailed Eagle
- **4 enclosures** — Kangaroo Paddock, Koala Corner, Penguin Cove, Reptile House
- **$10,000 AUD** starting balance
- **Ticket price** set to $25.00

The game has **no fixed end date** — play for as many days as you like and aim for the highest **Score** possible.

---

### 📊 Dashboard

The Dashboard is your central command centre, always showing:

| Element | What it means |
|---|---|
| **Balance** | Your current cash in AUD — never let it reach $0! |
| **Day** | How many days your zoo has been open |
| **Animals** | Number of living animals |
| **Score** | Your overall rating (see [Scoring](#-scoring--winning)) |
| **Health bar** | Average animal health (0–100) |
| **Hunger bar** | Average hunger (higher = more hungry = bad!) |
| **Happiness bar** | Average animal happiness (0–100) |

Bar colours:  🟢 **Green ≥ 70** = great  ·  🟠 **Orange 30–69** = caution  ·  🔴 **Red < 30** = take action now!

---

### 🔁 The Daily Loop

Each time you press **⏩ Advance Day**:

1. Every animal gets **+10 hunger** and **−3 happiness**
2. Every enclosure loses **10 cleanliness**
3. Visitors arrive and pay for tickets → revenue deposited
4. Breeding check fires — animals in shared enclosures may produce babies
5. Dead animals (health = 0) are removed
6. A **25% chance** of a random event (see [Random Events](#-random-events))
7. Your **Score** recalculates
8. The Daily Report popup summarises everything

**Your job:** before and after each day, keep animals fed, enclosures clean, and finances healthy.

---

### 🐾 Animals Tab

The treeview lists every living animal.  Click any column heading to sort.  Select a row to see
individual **canvas stat bars** in the detail panel.

#### Actions

| Button | What it does | Cost |
|---|---|---|
| 🍖 **Feed** | Reduces hunger, boosts happiness.  Requires food stock matching the animal's type. | ~$2–8 / unit consumed |
| 💊 **Medicate** | Restores health.  Choose a medicine type (see table below). | Per dose |
| 🎭 **Make Perform** | Triggers the animal's special ability (jump, swim, soar…) — boosts visitor satisfaction. | Free |
| 🚚 **Move** | Transfer to a different enclosure.  Pair same-species animals to enable breeding. | Free |
| 🛒 **Buy New** | Purchase a new animal from the market. | See table |

#### Animal Purchase Prices

| Species | Price (AUD) | Required Food | Special Ability |
|---|---|---|---|
| Snake | $250 | insects | slither() |
| Emu | $300 | grass | run() |
| Penguin | $350 | fish | swim(), waddle() |
| Koala | $400 | fruit / grass | climb() |
| Kangaroo | $500 | grass | jump(), box() |
| Eagle | $600 | meat | soar() |
| Crocodile | $800 | meat | snap() |

#### Daily Animal Mechanics

| What happens | Per day |
|---|---|
| Hunger increases | +10 |
| Happiness decreases | −3 |
| Consecutive hungry days (hunger > 80) | Health −10 per day after day 2 |
| Very unhappy (happiness < 20) | Health −5 per day |
| Health reaches 0 | Animal dies permanently |

> **Feed animals before hunger exceeds ~70** — at hunger > 80 for two days in a row, health
> starts dropping fast.

#### Medicine Reference

| Medicine | Cost / dose | HP restored | Best for |
|---|---|---|---|
| Antibiotic | $20 | +30 | Moderate illness |
| Vitamin | $8 | +10 | Maintenance / mild boost |
| Painkiller | $12 | +15 | Pain relief |
| **Vaccine** | **$25** | **+40** | **Best value — use after outbreaks** |

---

### 🏠 Enclosures Tab

| Action | Cost | Effect |
|---|---|---|
| 🧹 **Clean** | $50 | Restores cleanliness to 100 |
| 🔧 **Upgrade** | $500 | +1 upgrade level — improves animal happiness and visitor satisfaction |
| 🏗️ **Build New** | $1,000 + $2/m² | Creates a new enclosure of chosen habitat type |

#### Cleanliness Rules

- Enclosures lose **10 cleanliness per day**
- Below **30 cleanliness** → animals lose happiness
- Clean every 2–3 days to stay above 50

#### Breeding

When two animals of the **same species** share one enclosure there is a daily chance of a free
baby being born.  This is the cheapest way to grow your collection.

---

### 🛒 Resources Tab

Keep stock levels in the green.  Progress bars turn red when critically low.

#### Food Prices

| Food | Price / unit | Fed to |
|---|---|---|
| Grass | $2.00 | Kangaroos, Koalas, Emus |
| Fruit | $3.00 | Koalas |
| Insects | $1.50 | Snakes |
| Fish | $6.00 | Penguins |
| Meat | $8.00 | Crocodiles, Eagles |

> **Tip:** Buy grass and fruit in batches of 50+ (cheapest types).  Keep ≥5 vaccine doses in stock.

---

### 💰 Finances Tab

#### Revenue

- **Ticket sales** — daily visitors × ticket price.  Visitor count ≈ `20 + (avg_health / 5)` ± random variance.
- **Donations** — from Zoo Celebration and Donation Drive random events ($200–$2,000).

#### Setting Ticket Price

Higher price = more revenue per visitor.  But unhappy animals mean fewer visitors.
**Optimal range: $20–$35 AUD.**

#### Expense Categories

| Category | Typical cost |
|---|---|
| Animal purchase | $250–$800 per animal |
| Food | $1.50–$8.00 per unit |
| Medicine | $8–$25 per dose |
| Cleaning | $50 per enclosure |
| Enclosure upgrade | $500 per level |
| New enclosure | $1,000 + $2/m² |
| Escape fine (random) | $100–$500 |

> **Warning:** Balance below **$1,000 AUD** triggers a LOW FUNDS alert.  At $0 you cannot
> buy anything and the zoo will slowly collapse.

---

### ⚡ Random Events

Each day has a **25% chance** of triggering one random event:

| Event | Effect | Strategy |
|---|---|---|
| 🌡️ **Heatwave** | All animals −5 HP, −10 happiness | Feed and medicate immediately after |
| 🎉 **Zoo Celebration** | Bonus donation +$200–$800 | Great day — enjoy it! |
| 🚨 **Animal Escape** | Fine of $100–$500 | Keep $1,500+ buffer in the bank |
| 🦠 **Disease Outbreak** | One enclosure's animals lose 10–25 HP each | Vaccinate/medicate immediately |
| 💝 **Donation Drive** | Large donation +$300–$2,000 | Best event possible |
| 🍼 **Baby Boom** | 1–3 free baby animals added | Free growth — great! |

---

### 🏆 Scoring & Winning

Your **Score** recalculates every time you advance a day using this formula:

```
Score = avg_health    × 0.35
      + avg_happiness × 0.25
      + avg_visitor_satisfaction × 0.20
      + unique_species × 5
      + financial_score × 0.20

financial_score = min(100, balance / $1,000 × 10)
                  → $10,000 balance = perfect score of 100
```

#### Score Tiers

| Score | Rating |
|---|---|
| 0–49 | 😟 Struggling zoo — animals are suffering |
| 50–99 | 😐 Average zoo — room for improvement |
| 100–149 | 😊 Good zoo — visitors are happy |
| 150–199 | 😄 Great zoo — thriving animals and strong finances |
| **200+** | **🏆 Elite zoo — Australian wildlife paradise!** |

#### How to Maximise Your Score

1. Keep **all** animals at Health ≥ 70 and Hunger < 30
2. Clean enclosures every **2–3 days** ($50 each — cheap!)
3. Collect **all 7 species** for maximum diversity bonus (×5 pts each)
4. Keep your balance well above **$10,000** for the max financial score
5. Set ticket price at **$25–$30** for optimal visitor flow
6. **Breed** animals cheaply via shared enclosures (pair same species)
7. **Upgrade** enclosures to boost visitor satisfaction
8. After a Disease Outbreak, **vaccinate immediately** to prevent deaths

---

### 💡 Quick-Start Walkthrough

#### Day 0 (Before Advancing)

1. Open the **Animals** tab — all 8 animals start at full health (100 HP), hunger 0, happiness 80.
2. Note the **Dashboard**: Balance $10,000, Day 0, Score 0.
3. Optionally buy an extra species for early diversity bonus (try a Snake at $250).

#### Day 1

1. Press **⏩ Advance Day** — the Daily Report popup appears showing:
   - Visitor count and ticket revenue
   - Any births or random events
   - New balance and score
2. After closing the popup, check the **Animals** tab — hunger is now 10, happiness 77.
3. No action needed yet.  Advance another day.

#### Days 2–5

- **Feed every animal** as hunger approaches 70 (select animal → 🍖 Feed).
- Check **Enclosures** — cleanliness is dropping.  Clean any below 50 ($50).
- If a random event hit (heatwave/disease), medicate affected animals.
- Consider buying a second species (Penguin or Emu) for the +5 score bonus.

#### Days 6–15

- Experiment with **ticket price** on the Finances tab — try $28–$32.
- Put two Kangaroos or two Koalas in the **same enclosure** for free breeding.
- Build a second enclosure if you have more animals than capacity ($1,200+ for a 200 m² enclosure).
- Target **Score 100+** by day 10.

#### Long Term

- Collect all **7 species** for the maximum diversity bonus.
- Keep **$2,000+ cash buffer** to absorb escape fines and outbreaks.
- Target **Score 200+** by day 30.
- **💾 Save regularly** — save to `ozzoo_save.json` and reload anytime.

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
