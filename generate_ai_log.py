"""
generate_ai_log.py
------------------
Generates AI_Copilot_Usage_Log.pdf for the OzZoo project.
Run once from the repository root:
    python generate_ai_log.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
DARK_BLUE   = colors.HexColor("#1B3A6B")
MID_BLUE    = colors.HexColor("#2E6DA4")
LIGHT_BLUE  = colors.HexColor("#D6E8FA")
GREEN       = colors.HexColor("#1A7A4A")
LIGHT_GREEN = colors.HexColor("#D4EDDA")
AMBER       = colors.HexColor("#7A5200")
LIGHT_AMBER = colors.HexColor("#FFF3CD")
CODE_BG     = colors.HexColor("#F4F4F4")
CODE_BORDER = colors.HexColor("#CCCCCC")
TEXT_DARK   = colors.HexColor("#1A1A1A")
GREY        = colors.HexColor("#666666")

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
SS = getSampleStyleSheet()

def make_styles():
    styles = {}

    styles["title"] = ParagraphStyle(
        "title",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles["subtitle"] = ParagraphStyle(
        "subtitle",
        fontName="Helvetica",
        fontSize=11,
        textColor=colors.HexColor("#DDDDDD"),
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    styles["section_num"] = ParagraphStyle(
        "section_num",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=colors.white,
        alignment=TA_LEFT,
        leading=18,
    )
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=TEXT_DARK,
        leading=14,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
    )
    styles["label"] = ParagraphStyle(
        "label",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=MID_BLUE,
        spaceAfter=2,
        spaceBefore=6,
    )
    styles["label_green"] = ParagraphStyle(
        "label_green",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=GREEN,
        spaceAfter=2,
        spaceBefore=6,
    )
    styles["label_amber"] = ParagraphStyle(
        "label_amber",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=AMBER,
        spaceAfter=2,
        spaceBefore=6,
    )
    styles["code"] = ParagraphStyle(
        "code",
        fontName="Courier",
        fontSize=8,
        textColor=TEXT_DARK,
        leading=12,
        leftIndent=6,
    )
    styles["toc_entry"] = ParagraphStyle(
        "toc_entry",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=MID_BLUE,
        leading=16,
    )
    styles["footer"] = ParagraphStyle(
        "footer",
        fontName="Helvetica",
        fontSize=8,
        textColor=GREY,
        alignment=TA_CENTER,
    )
    styles["intro"] = ParagraphStyle(
        "intro",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=TEXT_DARK,
        leading=14,
        alignment=TA_JUSTIFY,
    )
    return styles


# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------

def header_table(entry_num: str, title: str, styles):
    """Coloured header row for each log entry."""
    data = [[
        Paragraph(f"Entry {entry_num}", styles["section_num"]),
        Paragraph(title, styles["section_num"]),
    ]]
    t = Table(data, colWidths=[2.5*cm, 14*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def prompt_box(text: str, styles):
    """Blue-tinted prompt box."""
    data = [[Paragraph(f'<b>Prompt:</b> "{text}"', styles["body"])]]
    t = Table(data, colWidths=[16.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 0.8, MID_BLUE),
        ("ROUNDEDCORNERS",(0, 0), (-1, -1), 4),
    ]))
    return t


def code_box(lines: list, styles):
    """Light-grey monospace code box."""
    content = "<br/>".join(lines)
    data = [[Paragraph(content, styles["code"])]]
    t = Table(data, colWidths=[16.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CODE_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 0.6, CODE_BORDER),
    ]))
    return t


def analysis_box(text: str, styles):
    """Green-tinted analysis box."""
    data = [[Paragraph(text, styles["body"])]]
    t = Table(data, colWidths=[16.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 0.8, GREEN),
    ]))
    return t


def modification_box(text: str, styles):
    """Amber-tinted modification / learning box."""
    data = [[Paragraph(text, styles["body"])]]
    t = Table(data, colWidths=[16.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_AMBER),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 0.8, AMBER),
    ]))
    return t


def add_entry(story, entry_num, title, purpose, prompt_text,
              ai_output_lines, analysis_text, modification_text, styles):
    """Assemble one complete log entry."""
    elems = [
        Spacer(1, 0.35*cm),
        header_table(entry_num, title, styles),
        Spacer(1, 0.2*cm),
        Paragraph(f"<b>Purpose:</b> {purpose}", styles["body"]),
        Spacer(1, 0.15*cm),
        Paragraph("KEY PROMPT", styles["label"]),
        prompt_box(prompt_text, styles),
        Spacer(1, 0.15*cm),
        Paragraph("AI OUTPUT SNIPPET", styles["label"]),
        code_box(ai_output_lines, styles),
        Spacer(1, 0.15*cm),
        Paragraph("YOUR ANALYSIS", styles["label_green"]),
        analysis_box(analysis_text, styles),
        Spacer(1, 0.1*cm),
        Paragraph("MODIFICATIONS &amp; LEARNING", styles["label_amber"]),
        modification_box(modification_text, styles),
        Spacer(1, 0.1*cm),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BBBBBB")),
    ]
    story.extend(elems)


# ---------------------------------------------------------------------------
# Log entry data
# ---------------------------------------------------------------------------

ENTRIES = [
    {
        "entry_num": "1",
        "title": "Project Architecture Design",
        "purpose": (
            "Before writing any code, I needed a clear OOP blueprint: which classes "
            "to create, how they relate, and what design patterns to apply."
        ),
        "prompt": (
            "Design a Python OOP zoo simulator called OzZoo. "
            "Identify all classes needed, their inheritance hierarchy, and any design patterns. "
            "Include animals (mammals, birds, reptiles), habitats, finance, and a top-level Zoo class."
        ),
        "ai_output": [
            "# Suggested class hierarchy",
            "Animal (ABC)  ←  abstract base",
            "  Mammal(Animal)  ←  intermediate",
            "    Lion(Mammal), Elephant(Mammal)  ←  concrete",
            "  Bird(Animal)   ←  intermediate",
            "    Eagle(Bird), Parrot(Bird)        ←  concrete",
            "  Reptile(Animal) ←  intermediate",
            "    Crocodile(Reptile), Gecko(Reptile) ← concrete",
            "",
            "Habitat   – standalone; owns animal roster + environment logic",
            "Finance   – Singleton (only ONE ledger per zoo)",
            "Zoo       – orchestrator; uses Habitat and Finance via composition",
        ],
        "analysis": (
            "The AI immediately produced a clean three-tier inheritance tree and correctly "
            "recommended the Singleton pattern for Finance and composition for Zoo. "
            "This saved significant up-front design time and gave a solid, testable structure "
            "that maps directly to real OOP principles taught in the course."
        ),
        "modification": (
            "I accepted the hierarchy as-is but added the Zoo class as the top-level "
            "orchestrator, which the AI had not explicitly included. I also decided to add "
            "a Habitat class with climate validation — an idea prompted by the AI's mention "
            "of 'environment logic'. Learned: AI excels at high-level design scaffolding."
        ),
    },
    {
        "entry_num": "2",
        "title": "Abstract Base Class with Encapsulation",
        "purpose": (
            "Implement the Animal ABC with properly encapsulated private attributes "
            "and @property descriptors so subclasses cannot bypass validation."
        ),
        "prompt": (
            "Write a Python abstract base class Animal with private attributes __health, "
            "__hunger, __happiness using double-underscore name mangling. Add @property "
            "getters and setters that clamp values between 0 and 100. Add abstract methods "
            "sound() and diet(). Add concrete methods feed(), play(), and receive_treatment()."
        ),
        "ai_output": [
            "from abc import ABC, abstractmethod",
            "",
            "class Animal(ABC):",
            "    _ticket_price: float = 10.0",
            "",
            "    def __init__(self, name, species, health=100, hunger=0, happiness=80):",
            "        self.__health = health",
            "        self.__hunger = hunger",
            "        self.__happiness = happiness",
            "",
            "    @property",
            "    def health(self) -> int:",
            "        return self.__health",
            "",
            "    @health.setter",
            "    def health(self, value: int) -> None:",
            "        self.__health = max(0, min(100, value))",
            "",
            "    @abstractmethod",
            "    def sound(self) -> str: ...",
            "",
            "    def feed(self, amount=20) -> str:",
            "        self.hunger -= amount",
            "        self.happiness += 5",
            "        return f'{self.name} has been fed.'",
        ],
        "analysis": (
            "The AI generated exactly the pattern needed: double-underscore mangling prevents "
            "direct access from outside the class, while the clamping setter (max/min) ensures "
            "stats never go out of range. The output was immediately usable and matched the "
            "encapsulation style required by the assignment."
        ),
        "modification": (
            "I added a public ticket_price property wrapping the protected _ticket_price class "
            "variable — the AI had left it as a bare class attribute, which would allow external "
            "code to access _ticket_price directly. I also added __name and __species as private "
            "attributes (the AI had left them public). Learned: always check that ALL attributes "
            "are properly encapsulated, not just the ones explicitly listed in the prompt."
        ),
    },
    {
        "entry_num": "3",
        "title": "Intermediate Inheritance Classes",
        "purpose": (
            "Create Mammal, Bird, and Reptile as intermediate classes that extend Animal "
            "and add group-specific attributes and behaviours before the concrete leaf classes."
        ),
        "prompt": (
            "Create three intermediate Python classes: Mammal(Animal), Bird(Animal), and "
            "Reptile(Animal). Each should add group-specific attributes (fur_colour, wingspan_cm, "
            "scale_colour etc.) and one new method (groom, fly, bask). Reptile should set "
            "is_warm_blooded = False as a class constant."
        ),
        "ai_output": [
            "class Mammal(Animal):",
            "    is_warm_blooded: bool = True",
            "",
            "    def __init__(self, name, species, fur_colour='brown', **kwargs):",
            "        super().__init__(name, species, **kwargs)",
            "        self.fur_colour = fur_colour",
            "",
            "    def groom(self) -> str:",
            "        self.happiness += 10",
            "        return f'{self.name} was groomed.'",
            "",
            "class Reptile(Animal):",
            "    is_warm_blooded: bool = False",
            "",
            "    def bask(self, minutes=30) -> str:",
            "        self.health += minutes // 10",
            "        return f'{self.name} basked for {minutes} min.'",
        ],
        "analysis": (
            "The AI correctly used super().__init__() with **kwargs to forward arguments up the "
            "chain — a pattern that is easy to get wrong. The is_warm_blooded class constant "
            "cleanly distinguishes warm- and cold-blooded animals without requiring runtime "
            "checks. The output required minimal changes."
        ),
        "modification": (
            "I added default implementations of sound() and diet() to each intermediate class "
            "so they are not accidentally left abstract — the AI had not included these, which "
            "would have made Mammal, Bird, and Reptile abstract too (unable to be instantiated "
            "for quick testing). Learned: always verify that intermediate classes satisfy the "
            "ABC contract."
        ),
    },
    {
        "entry_num": "4",
        "title": "Concrete Animal Classes",
        "purpose": (
            "Implement six concrete leaf classes — Lion, Elephant, Eagle, Parrot, Crocodile, "
            "Gecko — each with a unique species, ticket price, sound, diet, and at least one "
            "species-specific method."
        ),
        "prompt": (
            "Write a Python class Lion(Mammal) with species='Panthera leo', fur_colour='golden', "
            "ticket_price=$25, sound()='ROAR', diet()='carnivore', and a hunt() method that "
            "increases hunger by 20 and happiness by 10. Follow the same pattern for Elephant, "
            "Eagle, Parrot, Crocodile, and Gecko."
        ),
        "ai_output": [
            "class Lion(Mammal):",
            "    _ticket_price: float = 25.0",
            "",
            "    def __init__(self, name, is_male=True, mane_length='medium', **kwargs):",
            "        super().__init__(name=name, species='Panthera leo',",
            "                         fur_colour='golden', **kwargs)",
            "        self.is_male = is_male",
            "        self.mane_length = mane_length",
            "",
            "    def sound(self) -> str: return 'ROAR'",
            "    def diet(self)  -> str: return 'carnivore'",
            "",
            "    def hunt(self) -> str:",
            "        self.hunger += 20",
            "        self.happiness += 10",
            "        return f'{self.name} went on a hunt!'",
        ],
        "analysis": (
            "The AI produced consistent, idiomatic code for all six concrete classes in one "
            "pass. Hardcoding species, fur_colour, and ticket_price inside __init__ keeps each "
            "class self-contained. The **kwargs pattern ensures future attributes added to "
            "Animal or Mammal automatically flow through without changing the leaf classes."
        ),
        "modification": (
            "For Parrot, the AI generated talk() without randomness — I changed it to use "
            "random.choice(self.vocabulary) to make interactions more dynamic. For Gecko, I "
            "added a can_regrow_tail = True class constant as a fun biological detail. "
            "Learned: the AI gives correct structure but domain-specific details need "
            "human input."
        ),
    },
    {
        "entry_num": "5",
        "title": "Habitat Class with Climate Validation",
        "purpose": (
            "Build the Habitat class to manage animal rosters, enforce capacity limits, "
            "validate climate and enclosure type, and run a daily simulation loop."
        ),
        "prompt": (
            "Write a Python Habitat class with attributes: name, climate (validated against a "
            "tuple of allowed values), enclosure_type, capacity, area_sqm. It should have "
            "add_animal() and remove_animal() methods. Add a simulate_day() method that "
            "increases every animal's hunger by 5, gives reptiles in arid/tropical climates "
            "+3 health, and gives aquatic habitat animals +5 happiness."
        ),
        "ai_output": [
            "class Habitat:",
            "    VALID_CLIMATES   = ('tropical','arid','temperate','aquatic','arctic')",
            "    VALID_ENCLOSURES = ('open','cage','tank','aviary','terrarium')",
            "",
            "    def __init__(self, name, climate='temperate', ...):",
            "        if climate not in self.VALID_CLIMATES:",
            "            raise ValueError(f'Invalid climate {climate!r}.')",
            "        ...",
            "",
            "    def simulate_day(self) -> list[str]:",
            "        from ozzoo.animals.reptile import Reptile",
            "        log = []",
            "        for animal in self._animals:",
            "            animal.hunger += 5",
            "            if isinstance(animal, Reptile) and self.climate in ('arid','tropical'):",
            "                animal.health += 3",
            "            if self.climate == 'aquatic':",
            "                animal.happiness += 5",
            "        return log",
        ],
        "analysis": (
            "The AI correctly placed validation in __init__ using class-level tuple constants "
            "rather than magic strings scattered through methods. The deferred import of Reptile "
            "inside simulate_day() avoids a circular import — a subtlety the AI handled without "
            "being asked. The simulate_day() logic matches the specification exactly."
        ),
        "modification": (
            "I added log.append() calls inside the loop so the method returns a human-readable "
            "list of events (the AI returned an empty log). I also added a read-only animals "
            "property (returning list(self._animals)) so callers cannot mutate the internal "
            "list directly. Learned: AI often omits logging and copy-safety; always review "
            "return values carefully."
        ),
    },
    {
        "entry_num": "6",
        "title": "Finance Singleton Pattern",
        "purpose": (
            "Implement a Finance class that guarantees only ONE instance exists across the "
            "entire application, using Python's __new__ and an _initialised guard."
        ),
        "prompt": (
            "Write a Python Finance class implementing the Singleton pattern using __new__. "
            "It should have private attributes __balance (starting at 50000), __revenue, and "
            "__expenses, all exposed via @property. Include methods: charge_admission(), "
            "pay_food_bill(), pay_vet_bill(), record_expense(), record_income(), and report(). "
            "Add a class method reset() for test isolation."
        ),
        "ai_output": [
            "class Finance:",
            "    _instance: Finance | None = None",
            "    _initialised: bool = False",
            "",
            "    def __new__(cls) -> Finance:",
            "        if cls._instance is None:",
            "            cls._instance = super().__new__(cls)",
            "        return cls._instance",
            "",
            "    def __init__(self) -> None:",
            "        if self._initialised: return",
            "        self.__balance  = 50_000.0",
            "        self.__revenue  = 0.0",
            "        self.__expenses = 0.0",
            "        self._initialised = True",
            "",
            "    @classmethod",
            "    def reset(cls) -> None:",
            "        cls._instance     = None",
            "        cls._initialised  = False",
        ],
        "analysis": (
            "The AI produced a textbook Singleton with the _initialised guard — critical to "
            "prevent __init__ from resetting the balance on every Finance() call. The reset() "
            "classmethod is an important addition for unit testing that many Singleton examples "
            "omit. The output was used verbatim with no structural changes."
        ),
        "modification": (
            "No structural changes were needed. I did verify the singleton by adding "
            "'f1 = Finance(); f2 = Finance(); assert f1 is f2' to main.py — the AI suggested "
            "this test pattern when I asked. Learned: the Singleton pattern in Python is "
            "clean when __new__ and _initialised work together; memorise this idiom."
        ),
    },
    {
        "entry_num": "7",
        "title": "Zoo Orchestrator (Composition over Inheritance)",
        "purpose": (
            "Build the top-level Zoo class that wires Habitats and Finance together using "
            "composition, providing high-level operations like admit_visitors() and simulate_day()."
        ),
        "prompt": (
            "Write a Zoo class that owns a list of Habitat objects and a reference to the "
            "Finance singleton. Do NOT use inheritance — use composition. Include add_habitat(), "
            "place_animal(), admit_visitors(count), simulate_day(), and full_report(). "
            "admit_visitors should charge each animal's ticket_price via Finance."
        ),
        "ai_output": [
            "class Zoo:",
            "    def __init__(self, name, location='Sydney, Australia'):",
            "        self.name = name",
            "        self.location = location",
            "        self._habitats: list[Habitat] = []",
            "        self._finance: Finance = Finance()",
            "",
            "    def admit_visitors(self, count=1) -> list[str]:",
            "        log = []",
            "        for habitat in self._habitats:",
            "            for animal in habitat.animals:",
            "                msg = self._finance.charge_admission(",
            "                          animal._ticket_price, count)",
            "                log.append(f'[{habitat.name}] {animal.name}: {msg}')",
            "        return log",
        ],
        "analysis": (
            "The AI correctly modelled Zoo as a composition class with no custom parent, "
            "and naturally used Finance() to obtain the singleton rather than passing it in. "
            "The full_report() method it generated aggregates all habitat reports and the "
            "finance report into a single printable string — very useful for demos."
        ),
        "modification": (
            "The AI accessed animal._ticket_price (a protected attribute) directly inside "
            "Zoo. I changed this to animal.ticket_price (the public property added to Animal) "
            "to respect encapsulation. I also moved simulate_day() to deduct daily operating "
            "costs per habitat ($500 each) — the AI had not included this. Learned: always "
            "check that cross-class access respects the access modifiers you defined."
        ),
    },
    {
        "entry_num": "8",
        "title": "Debugging — Encapsulation Violation Fix",
        "purpose": (
            "During code review the AI flagged that Zoo was directly reading animal._ticket_price "
            "(a protected attribute), breaking encapsulation. I used the AI to find the cleanest fix."
        ),
        "prompt": (
            "In my Zoo class I am accessing animal._ticket_price directly. How do I fix this to "
            "respect encapsulation without changing the existing _ticket_price class variable "
            "on Animal and its subclasses?"
        ),
        "ai_output": [
            "# Add a public property to Animal:",
            "@property",
            "def ticket_price(self) -> float:",
            "    return self._ticket_price",
            "",
            "# Then in Zoo, replace:",
            "#   animal._ticket_price",
            "# with:",
            "#   animal.ticket_price",
            "",
            "# This keeps _ticket_price as the class-level override point",
            "# while exposing a clean public API.",
        ],
        "analysis": (
            "This was a targeted debugging session. The AI identified the root cause "
            "immediately and suggested adding a thin property wrapper — the minimal change "
            "that fixes the encapsulation violation without requiring any refactor of the "
            "existing subclass _ticket_price overrides. The suggestion was correct and clean."
        ),
        "modification": (
            "I implemented the fix exactly as suggested (added ticket_price property to "
            "Animal, updated Zoo.admit_visitors). No further changes were needed. "
            "Learned: when encapsulation is violated across class boundaries, a single "
            "property getter is often the smallest correct fix. AI is particularly good "
            "at these surgical 'find the minimal change' queries."
        ),
    },
]


# ---------------------------------------------------------------------------
# Build PDF
# ---------------------------------------------------------------------------

def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=1.8*cm,
        bottomMargin=2*cm,
        title="AI Copilot Usage Log – OzZoo",
        author="Manan Sharma",
        subject="AI Copilot Usage Log",
    )

    styles = make_styles()
    story = []

    # ---- Cover / title block -----------------------------------------------
    cover_data = [[
        Paragraph("AI Copilot Usage Log", styles["title"]),
    ], [
        Paragraph("Project: OzZoo – Object-Oriented Virtual Zoo Simulator", styles["subtitle"]),
    ], [
        Paragraph("Author: Manan Sharma  |  Student ID: BSIT 2023-2026, VSIT Mumbai", styles["subtitle"]),
    ], [
        Paragraph("Date: March 2026  |  Tool: GitHub Copilot / GPT-based AI assistant", styles["subtitle"]),
    ]]
    cover = Table(cover_data, colWidths=[16.5*cm])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
    ]))
    story.append(cover)
    story.append(Spacer(1, 0.4*cm))

    # ---- Introduction -------------------------------------------------------
    intro_text = (
        "This log documents my use of an AI coding assistant (GitHub Copilot / GPT) during "
        "the development of <b>OzZoo</b>, a Python object-oriented virtual zoo simulator. "
        "The project implements 13 classes across a four-level inheritance hierarchy, a "
        "Singleton design pattern (Finance), and a composition-based orchestrator (Zoo). "
        "<br/><br/>"
        "Each entry below records: the <b>key prompt</b> I submitted, a representative "
        "<b>AI output snippet</b>, and my <b>analysis</b> explaining why the prompt was "
        "used, how helpful the output was, what I modified, and what I learned."
    )
    intro_data = [[Paragraph(intro_text, styles["intro"])]]
    intro_table = Table(intro_data, colWidths=[16.5*cm])
    intro_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#EEF4FB")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 0.8, MID_BLUE),
    ]))
    story.append(intro_table)
    story.append(Spacer(1, 0.3*cm))

    # ---- Legend / colour key ------------------------------------------------
    legend_rows = [
        [
            Paragraph("<b>Colour Legend</b>", styles["body"]),
            Paragraph("Blue = Key Prompt", styles["body"]),
            Paragraph("Grey = AI Output", styles["body"]),
            Paragraph("Green = Analysis", styles["body"]),
            Paragraph("Amber = Modifications &amp; Learning", styles["body"]),
        ]
    ]
    legend = Table(legend_rows, colWidths=[3*cm, 3*cm, 3*cm, 3.5*cm, 4*cm])
    legend.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), DARK_BLUE),
        ("TEXTCOLOR",     (0, 0), (0, 0), colors.white),
        ("BACKGROUND",    (1, 0), (1, 0), LIGHT_BLUE),
        ("BACKGROUND",    (2, 0), (2, 0), CODE_BG),
        ("BACKGROUND",    (3, 0), (3, 0), LIGHT_GREEN),
        ("BACKGROUND",    (4, 0), (4, 0), LIGHT_AMBER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BOX",           (0, 0), (-1, -1), 0.5, GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, GREY),
    ]))
    story.append(legend)
    story.append(Spacer(1, 0.2*cm))
    story.append(HRFlowable(width="100%", thickness=1.2, color=DARK_BLUE))

    # ---- Log entries --------------------------------------------------------
    for entry in ENTRIES:
        add_entry(
            story,
            entry_num=entry["entry_num"],
            title=entry["title"],
            purpose=entry["purpose"],
            prompt_text=entry["prompt"],
            ai_output_lines=entry["ai_output"],
            analysis_text=entry["analysis"],
            modification_text=entry["modification"],
            styles=styles,
        )

    # ---- Summary table ------------------------------------------------------
    story.append(Spacer(1, 0.4*cm))
    sum_header = Table(
        [[Paragraph("Summary: AI Contribution vs. Human Modifications", styles["section_num"])]],
        colWidths=[16.5*cm]
    )
    sum_header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story.append(sum_header)
    story.append(Spacer(1, 0.2*cm))

    sum_rows = [
        ["Entry", "AI Contribution", "Key Human Modification"],
        ["1 – Architecture", "Full class hierarchy + pattern selection", "Added Zoo orchestrator class"],
        ["2 – Animal ABC", "Encapsulation, properties, abstract methods", "Added ticket_price property; made __name private"],
        ["3 – Intermediate", "super() chain with **kwargs; class constants", "Added default sound()/diet() implementations"],
        ["4 – Concrete Animals", "Consistent structure across 6 classes", "Added randomness to Parrot; Gecko biology detail"],
        ["5 – Habitat", "Climate validation; deferred import; simulate_day()", "Added log messages; copy-safe animals property"],
        ["6 – Finance", "Singleton __new__ + guard; reset() for tests", "Used verbatim; verified with assert test"],
        ["7 – Zoo", "Composition design; full_report()", "Fixed _ticket_price access; added operating costs"],
        ["8 – Debug Fix", "Minimal property-wrapper solution", "Implemented fix across Animal + Zoo"],
    ]

    col_widths = [3.2*cm, 7.5*cm, 5.8*cm]
    sum_table = Table(sum_rows, colWidths=col_widths, repeatRows=1)
    sum_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), MID_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F8")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(sum_table)

    story.append(Spacer(1, 0.4*cm))
    closing = (
        "<b>Overall Reflection:</b> The AI copilot was most valuable for boilerplate generation "
        "(class scaffolding, property descriptors, design patterns) and for targeted debugging "
        "('find the minimal fix'). Human judgement was essential for domain details, logging "
        "completeness, copy-safety, and enforcing consistent encapsulation across class "
        "boundaries. Critical engagement — verifying every output before accepting it — "
        "was the key skill practised throughout this project."
    )
    story.append(analysis_box(closing, styles))

    # ---- Build ---------------------------------------------------------------
    doc.build(story)
    print(f"[OK] PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf("AI_Copilot_Usage_Log.pdf")
