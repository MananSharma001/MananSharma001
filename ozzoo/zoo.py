"""
zoo.py
======
Top-level ``Zoo`` class — the central manager for the entire OzZoo simulation.

The ``Zoo`` owns:
- All :class:`~animals.animal.Animal` instances
- All :class:`~enclosure.Enclosure` instances
- All :class:`~habitat.Habitat` instances
- The :class:`~finance.Finance` singleton
- :class:`~food.FoodInventory` and :class:`~medicine.MedicineInventory`
- The :class:`~patterns.observer.ZooEventManager` for event broadcasting
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from animals.animal import Animal
from enclosure import Enclosure
from habitat import Habitat
from finance import Finance
from food import FoodInventory
from medicine import MedicineInventory
from visitor import Visitor, generate_visitors
from patterns.observer import ZooEventManager, WelfareObserver, FinanceObserver, EventLogger
from patterns.factory import AnimalFactory
from exceptions import (
    AnimalNotFoundError,
    InsufficientFundsError,
    InsufficientFoodError,
    HabitatCapacityExceededError,
    IncompatibleSpeciesError,
    InvalidActionError,
)


class Zoo:
    """
    Top-level manager for the OzZoo simulation.

    Coordinates animals, enclosures, habitats, visitors, finances,
    food/medicine inventory, and the event system.

    Parameters
    ----------
    name : str
        Name of the zoo.  Defaults to ``"OzZoo"``.
    """

    WELFARE_HEALTH_THRESHOLD: int = 30
    FINANCE_CRITICAL_THRESHOLD: float = 1000.0
    DEFAULT_TICKET_PRICE: float = 25.0

    def __init__(self, name: str = "OzZoo") -> None:
        """Initialise the zoo with default resources and starting animals."""
        self._name: str = name
        self._day: int = 0
        self._ticket_price: float = self.DEFAULT_TICKET_PRICE
        self._score: int = 0

        # Core resources
        self._finance: Finance = Finance.get_instance()
        self._food: FoodInventory = FoodInventory()
        self._medicine: MedicineInventory = MedicineInventory()

        # Zoo entities
        self._animals: List[Animal] = []
        self._enclosures: List[Enclosure] = []
        self._habitats: List[Habitat] = []
        self._daily_visitors: List[Visitor] = []

        # Statistics
        self._total_visitors: int = 0
        self._total_income: float = 0.0
        self._animals_born: int = 0
        self._animals_died: int = 0

        # Observer event system
        self._event_manager: ZooEventManager = ZooEventManager()
        self._welfare_observer: WelfareObserver = WelfareObserver()
        self._finance_observer: FinanceObserver = FinanceObserver(
            threshold=self.FINANCE_CRITICAL_THRESHOLD
        )
        self._event_logger: EventLogger = EventLogger()

        # Wire up observers
        self._event_manager.subscribe("animal_health_critical", self._welfare_observer)
        self._event_manager.subscribe("animal_health_critical", self._event_logger)
        self._event_manager.subscribe("low_funds", self._finance_observer)
        self._event_manager.subscribe("low_funds", self._event_logger)
        self._event_manager.subscribe("animal_born", self._event_logger)
        self._event_manager.subscribe("animal_died", self._event_logger)
        self._event_manager.subscribe("random_event", self._event_logger)

        # Set up starting zoo
        self._initialise_zoo()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _initialise_zoo(self) -> None:
        """Create the starting habitats, enclosures, and animals."""
        # Habitats
        savannah = Habitat("HAB-001", "Australian Outback", "Savannah",
                           "Open grasslands of the Australian interior.")
        arctic = Habitat("HAB-002", "Antarctic Zone", "Arctic",
                         "Icy habitat for cold-climate species.")
        wetlands = Habitat("HAB-003", "Wetlands Reserve", "Wetlands",
                           "Tropical wetlands teeming with wildlife.")
        forest = Habitat("HAB-004", "Eucalyptus Forest", "Forest",
                         "Dense forests of native gum trees.")

        # Enclosures
        enc_savannah = Enclosure("ENC-001", "Savannah Plains", "Savannah",
                                  max_capacity=6, area_m2=500.0)
        enc_arctic = Enclosure("ENC-002", "Penguin Cove", "Arctic",
                                max_capacity=8, area_m2=300.0)
        enc_wetlands = Enclosure("ENC-003", "Croc Creek", "Wetlands",
                                  max_capacity=4, area_m2=400.0)
        enc_forest = Enclosure("ENC-004", "Koala Corner", "Forest",
                                max_capacity=6, area_m2=250.0)

        savannah.add_enclosure(enc_savannah)
        arctic.add_enclosure(enc_arctic)
        wetlands.add_enclosure(enc_wetlands)
        forest.add_enclosure(enc_forest)

        self._habitats = [savannah, arctic, wetlands, forest]
        self._enclosures = [enc_savannah, enc_arctic, enc_wetlands, enc_forest]

        # Starting animals
        starting: List[Tuple[str, str]] = [
            ("kangaroo", "Skippy"),
            ("kangaroo", "Matilda"),
            ("koala", "Bindi"),
            ("koala", "Koby"),
            ("penguin", "Percy"),
            ("penguin", "Priscilla"),
            ("crocodile", "Crunch"),
            ("eagle", "Aria"),
        ]
        for species, animal_name in starting:
            animal = AnimalFactory.create_animal(species, animal_name, age=random.randint(1, 5))
            self._animals.append(animal)

        # Place animals into appropriate enclosures
        placement: Dict[str, str] = {
            "Savannah": "ENC-001",
            "Arctic": "ENC-002",
            "Wetlands": "ENC-003",
            "Forest": "ENC-004",
        }
        for animal in self._animals:
            enc_id = placement.get(animal.habitat_type)
            if enc_id:
                enc = self.get_enclosure_by_id(enc_id)
                if enc:
                    try:
                        enc.add_animal(animal)
                    except (HabitatCapacityExceededError, IncompatibleSpeciesError):
                        pass  # best-effort on startup

    # ------------------------------------------------------------------
    # Animal management
    # ------------------------------------------------------------------

    def get_all_animals(self) -> List[Animal]:
        """
        Return the list of all animals in the zoo (alive and dead).

        Returns
        -------
        List[Animal]
            All registered animals.
        """
        return list(self._animals)

    def get_alive_animals(self) -> List[Animal]:
        """
        Return only living animals.

        Returns
        -------
        List[Animal]
            Animals where ``is_alive`` is ``True``.
        """
        return [a for a in self._animals if a.is_alive]

    def find_animal(self, name: str) -> Animal:
        """
        Find an animal by name (case-insensitive).

        Parameters
        ----------
        name : str
            The animal's name to search for.

        Returns
        -------
        Animal
            The matching animal.

        Raises
        ------
        AnimalNotFoundError
            If no animal with that name exists.
        """
        for animal in self._animals:
            if animal.name.lower() == name.lower():
                return animal
        raise AnimalNotFoundError(f"No animal named '{name}' found in the zoo.")

    def buy_animal(self, species: str, name: str, age: int = 1) -> str:
        """
        Buy a new animal and add it to the zoo's roster.

        Parameters
        ----------
        species : str
            Species key supported by :class:`~patterns.factory.AnimalFactory`.
        name : str
            Name for the new animal.
        age : int
            Age in years.

        Returns
        -------
        str
            Confirmation message.

        Raises
        ------
        InsufficientFundsError
            If the zoo cannot afford the purchase.
        """
        # Cost varies by species
        costs: Dict[str, float] = {
            "kangaroo": 500.0, "koala": 400.0,
            "penguin": 350.0, "emu": 300.0,
            "crocodile": 800.0, "eagle": 600.0,
            "snake": 250.0,
        }
        cost = costs.get(species.lower(), 400.0)
        self._finance.deduct_expense(cost, "animal_purchase",
                                     f"Bought {species} named {name}")
        animal = AnimalFactory.create_animal(species, name, age=age)
        self._animals.append(animal)
        self._event_manager.notify(
            "random_event",
            {"message": f"New {species} '{name}' purchased for ${cost:.2f}"},
        )
        return f"🎉 {name} the {species} has joined OzZoo! (Cost: ${cost:.2f} AUD)"

    def move_animal_to_enclosure(self, animal_name: str, enclosure_id: str) -> str:
        """
        Move an animal to a different enclosure.

        Parameters
        ----------
        animal_name : str
            Name of the animal to move.
        enclosure_id : str
            ID of the target enclosure.

        Returns
        -------
        str
            Confirmation message.

        Raises
        ------
        AnimalNotFoundError
            If the animal does not exist.
        HabitatCapacityExceededError
            If the target enclosure is full.
        IncompatibleSpeciesError
            If the target enclosure is the wrong habitat type.
        """
        animal = self.find_animal(animal_name)
        target = self.get_enclosure_by_id(enclosure_id)
        if target is None:
            raise InvalidActionError(f"Enclosure '{enclosure_id}' not found.")

        # Remove from current enclosure
        for enc in self._enclosures:
            enc.remove_animal(animal)

        return target.add_animal(animal)

    def feed_animal(self, animal_name: str) -> str:
        """
        Feed a named animal using the zoo's food inventory.

        Parameters
        ----------
        animal_name : str
            Name of the animal to feed.

        Returns
        -------
        str
            Feeding result message.

        Raises
        ------
        AnimalNotFoundError
            If the animal is not found.
        InsufficientFoodError
            If there is no food stock.
        InvalidActionError
            If the animal is already full (hunger < 20).
        """
        animal = self.find_animal(animal_name)
        if not animal.is_alive:
            raise InvalidActionError(f"{animal_name} is no longer alive.")
        if animal.hunger < 20:
            raise InvalidActionError(
                f"{animal_name} is not hungry enough (hunger={animal.hunger})."
            )

        food_type = animal.required_food
        try:
            self._food.consume(food_type, units=1)
        except InsufficientFoodError as e:
            raise InsufficientFoodError(str(e)) from e

        return animal.eat(1)

    def medicate_animal(
        self, animal_name: str, medicine_type: str = "antibiotic"
    ) -> str:
        """
        Administer medicine to a named animal.

        Parameters
        ----------
        animal_name : str
            Name of the animal to treat.
        medicine_type : str
            Type of medicine from the inventory.  Defaults to ``"antibiotic"``.

        Returns
        -------
        str
            Treatment result message.

        Raises
        ------
        AnimalNotFoundError
            If the animal is not found.
        ValueError
            If medicine stock is insufficient.
        """
        animal = self.find_animal(animal_name)
        if not animal.is_alive:
            raise InvalidActionError(f"{animal_name} is no longer alive.")
        heal = self._medicine.administer(medicine_type, doses=1)
        return animal.apply_medicine(heal)

    # ------------------------------------------------------------------
    # Enclosure management
    # ------------------------------------------------------------------

    def get_enclosure_by_id(self, enclosure_id: str) -> Optional[Enclosure]:
        """
        Find an enclosure by its ID.

        Parameters
        ----------
        enclosure_id : str
            The enclosure ID to search for.

        Returns
        -------
        Optional[Enclosure]
            Matching enclosure or ``None``.
        """
        for enc in self._enclosures:
            if enc.enclosure_id == enclosure_id:
                return enc
        return None

    def build_enclosure(
        self,
        name: str,
        habitat_type: str,
        max_capacity: int = 5,
        area_m2: float = 200.0,
    ) -> str:
        """
        Build a new enclosure and add it to the zoo.

        Parameters
        ----------
        name : str
            Name for the new enclosure.
        habitat_type : str
            Habitat type for the enclosure.
        max_capacity : int
            Maximum animal capacity.
        area_m2 : float
            Floor area in square metres.

        Returns
        -------
        str
            Confirmation message.

        Raises
        ------
        InsufficientFundsError
            If the zoo cannot afford construction.
        """
        cost = 1000.0 + (area_m2 * 2.0)
        self._finance.deduct_expense(cost, "construction",
                                     f"Built new {habitat_type} enclosure: {name}")
        enc_id = f"ENC-{len(self._enclosures) + 1:03d}"
        enc = Enclosure(enc_id, name, habitat_type, max_capacity, area_m2)
        self._enclosures.append(enc)

        # Add to matching habitat if one exists
        for hab in self._habitats:
            if hab.habitat_type == habitat_type:
                hab.add_enclosure(enc)
                break
        else:
            # Create a new habitat
            hab_id = f"HAB-{len(self._habitats) + 1:03d}"
            hab = Habitat(hab_id, f"{habitat_type} Zone", habitat_type)
            hab.add_enclosure(enc)
            self._habitats.append(hab)

        return (
            f"🏗️  New enclosure '{name}' built! "
            f"(ID: {enc_id}, type: {habitat_type}, capacity: {max_capacity}, "
            f"cost: ${cost:.2f} AUD)"
        )

    def clean_enclosure(self, enclosure_id: str) -> str:
        """
        Clean an enclosure and deduct the cleaning cost.

        Parameters
        ----------
        enclosure_id : str
            ID of the enclosure to clean.

        Returns
        -------
        str
            Cleaning result message.

        Raises
        ------
        InvalidActionError
            If the enclosure is not found.
        """
        enc = self.get_enclosure_by_id(enclosure_id)
        if enc is None:
            raise InvalidActionError(f"Enclosure '{enclosure_id}' not found.")
        cost = 50.0
        self._finance.deduct_expense(cost, "maintenance", f"Cleaned {enc.name}")
        return enc.clean() + f" (Cost: ${cost:.2f} AUD)"

    def upgrade_enclosure(self, enclosure_id: str) -> str:
        """
        Upgrade an enclosure.

        Parameters
        ----------
        enclosure_id : str
            ID of the enclosure to upgrade.

        Returns
        -------
        str
            Upgrade result message.

        Raises
        ------
        InvalidActionError
            If the enclosure is not found.
        InsufficientFundsError
            If funds are insufficient.
        """
        enc = self.get_enclosure_by_id(enclosure_id)
        if enc is None:
            raise InvalidActionError(f"Enclosure '{enclosure_id}' not found.")
        cost = Enclosure.UPGRADE_COST
        self._finance.deduct_expense(cost, "upgrades", f"Upgraded {enc.name}")
        return enc.upgrade() + f" (Cost: ${cost:.2f} AUD)"

    # ------------------------------------------------------------------
    # Resource management
    # ------------------------------------------------------------------

    def buy_food(self, food_type: str, units: int) -> str:
        """
        Purchase food stock.

        Parameters
        ----------
        food_type : str
            Food category to purchase.
        units : int
            Number of units to buy.

        Returns
        -------
        str
            Purchase confirmation message.

        Raises
        ------
        InsufficientFundsError
            If the zoo cannot afford the purchase.
        ValueError
            If the food type is invalid.
        """
        cost = self._food.purchase(food_type, units)
        self._finance.deduct_expense(cost, "food",
                                     f"Purchased {units} units of {food_type}")
        return f"🛒 Bought {units} units of {food_type} for ${cost:.2f} AUD."

    def buy_medicine(self, medicine_type: str, doses: int) -> str:
        """
        Purchase medicine stock.

        Parameters
        ----------
        medicine_type : str
            Medicine category to purchase.
        doses : int
            Number of doses to buy.

        Returns
        -------
        str
            Purchase confirmation message.

        Raises
        ------
        InsufficientFundsError
            If the zoo cannot afford the purchase.
        ValueError
            If the medicine type is invalid.
        """
        cost = self._medicine.purchase(medicine_type, doses)
        self._finance.deduct_expense(cost, "medicine",
                                     f"Purchased {doses} doses of {medicine_type}")
        return f"💊 Bought {doses} dose(s) of {medicine_type} for ${cost:.2f} AUD."

    # ------------------------------------------------------------------
    # Finance
    # ------------------------------------------------------------------

    def set_ticket_price(self, price: float) -> str:
        """
        Set a new ticket price.

        Parameters
        ----------
        price : float
            New ticket price in AUD (must be > 0 and <= 500).

        Returns
        -------
        str
            Confirmation message.

        Raises
        ------
        InvalidActionError
            If the price is out of the acceptable range.
        """
        if price <= 0 or price > 500:
            raise InvalidActionError("Ticket price must be between $0.01 and $500.00.")
        old = self._ticket_price
        self._ticket_price = price
        return f"🎟️  Ticket price updated: ${old:.2f} → ${price:.2f} AUD"

    # ------------------------------------------------------------------
    # Daily simulation helpers
    # ------------------------------------------------------------------

    def _process_visitors(self) -> Tuple[int, float]:
        """
        Generate daily visitors and collect ticket revenue.

        Returns
        -------
        Tuple[int, float]
            (visitor_count, ticket_revenue)
        """
        # Base visitors influenced by animal welfare and happiness
        alive = self.get_alive_animals()
        avg_health = (sum(a.health for a in alive) / len(alive)) if alive else 50
        base = max(5, int(20 + (avg_health / 5)))
        count = random.randint(max(1, base - 10), base + 20)

        visitors = generate_visitors(count, self._ticket_price)
        self._daily_visitors = visitors
        self._total_visitors += count

        revenue = count * self._ticket_price
        self._finance.add_income(revenue, "ticket_sales",
                                 f"Day {self._day}: {count} visitors")
        self._total_income += revenue
        return count, revenue

    def _check_welfare(self) -> None:
        """Notify observers if any animal's health is critically low."""
        for animal in self.get_alive_animals():
            if animal.health < self.WELFARE_HEALTH_THRESHOLD:
                self._event_manager.notify(
                    "animal_health_critical",
                    {
                        "animal_name": animal.name,
                        "species": animal.species,
                        "health": animal.health,
                        "day": self._day,
                    },
                )

    def _check_finances(self) -> None:
        """Notify finance observer if balance is critically low."""
        balance = self._finance.get_balance()
        if balance < self.FINANCE_CRITICAL_THRESHOLD:
            self._event_manager.notify(
                "low_funds",
                {"balance": balance, "threshold": self.FINANCE_CRITICAL_THRESHOLD},
            )

    def _check_deaths(self) -> list[str]:
        """
        Remove dead animals from enclosures and log events.

        Returns
        -------
        list[str]
            Death event messages.
        """
        events: list[str] = []
        for animal in self._animals:
            if not animal.is_alive:
                for enc in self._enclosures:
                    result = enc.remove_animal(animal)
                    if result:
                        events.append(result)
                self._animals_died += 1
                self._event_manager.notify(
                    "animal_died",
                    {"animal_name": animal.name, "species": animal.species, "day": self._day},
                )
        # Clean up dead animals from the main list
        self._animals = [a for a in self._animals if a.is_alive]
        return events

    def _trigger_random_event(self) -> Optional[str]:
        """
        Possibly trigger a random event.  Called once per day tick.

        Returns
        -------
        Optional[str]
            Event description, or ``None`` if no event fired.
        """
        if random.random() > 0.25:  # 25% chance of a random event
            return None

        events = [
            self._event_heatwave,
            self._event_celebration,
            self._event_escape,
            self._event_disease_outbreak,
            self._event_donation_drive,
            self._event_baby_boom,
        ]
        return random.choice(events)()

    def _event_heatwave(self) -> str:
        """Heatwave — animals suffer, visitors stay away."""
        msg = "🌡️  RANDOM EVENT: HEATWAVE!  Temperatures soar — animals struggle."
        for animal in self.get_alive_animals():
            animal.happiness = animal.happiness - 10
            animal.health = animal.health - 5
        self._event_manager.notify("random_event", {"message": msg})
        return msg

    def _event_celebration(self) -> str:
        """Zoo celebration — visitor count doubles, donations pour in."""
        bonus = random.uniform(200, 800)
        self._finance.add_income(bonus, "donation", "Zoo Celebration donations")
        msg = (
            f"🎉 RANDOM EVENT: ZOO CELEBRATION!  "
            f"Crowds flock in!  Donations: +${bonus:.2f} AUD"
        )
        self._event_manager.notify("random_event", {"message": msg})
        return msg

    def _event_escape(self) -> str:
        """Animal escape — costs money to recapture."""
        alive = self.get_alive_animals()
        if not alive:
            return "🔒 All animals are safely secured."
        escapee = random.choice(alive)
        cost = random.uniform(100, 500)
        try:
            self._finance.deduct_expense(cost, "fines",
                                         f"{escapee.name} escape recapture")
        except InsufficientFundsError:
            pass  # Zoo is broke but life goes on
        msg = (
            f"🚨 RANDOM EVENT: ANIMAL ESCAPE!  {escapee.name} "
            f"escaped but was recaptured!  Cost: ${cost:.2f} AUD"
        )
        self._event_manager.notify("random_event", {"message": msg})
        return msg

    def _event_disease_outbreak(self) -> str:
        """Disease outbreak — random animals in one enclosure get sick."""
        if not self._enclosures:
            return ""
        enc = random.choice(self._enclosures)
        affected: list[str] = []
        for animal in enc.animals:
            if animal.is_alive:
                animal.health = animal.health - random.randint(10, 25)
                affected.append(animal.name)
        msg = (
            f"🦠 RANDOM EVENT: DISEASE OUTBREAK in {enc.name}!  "
            f"Affected: {', '.join(affected) or 'none'}"
        )
        self._event_manager.notify("random_event", {"message": msg})
        return msg

    def _event_donation_drive(self) -> str:
        """Generous donor — large donation received."""
        amount = random.uniform(300, 2000)
        self._finance.add_income(amount, "donation", "Donation drive")
        msg = f"💝 RANDOM EVENT: DONATION DRIVE!  Received ${amount:.2f} AUD in donations!"
        self._event_manager.notify("random_event", {"message": msg})
        return msg

    def _event_baby_boom(self) -> str:
        """Baby boom — multiple random births."""
        babies = random.randint(1, 3)
        species_list = ["kangaroo", "koala", "penguin"]
        born: list[str] = []
        for _ in range(babies):
            sp = random.choice(species_list)
            try:
                baby = AnimalFactory.create_animal(sp, f"Baby_{sp.capitalize()}", age=0)
                self._animals.append(baby)
                born.append(baby.name)
                self._animals_born += 1
            except Exception:
                pass
        msg = (
            f"🍼 RANDOM EVENT: BABY BOOM!  "
            f"New arrivals: {', '.join(born) or 'none'}"
        )
        self._event_manager.notify("animal_born",
                                   {"animals": born, "day": self._day})
        return msg

    # ------------------------------------------------------------------
    # Day advancement
    # ------------------------------------------------------------------

    def advance_day(self) -> Dict:
        """
        Advance the simulation by one day.

        Runs all daily ticks: animal welfare, habitats, enclosures,
        visitors, breeding, random events, and financial checks.

        Returns
        -------
        Dict
            Summary of what happened today.
        """
        self._day += 1
        summary: Dict = {
            "day": self._day,
            "events": [],
            "visitors": 0,
            "revenue": 0.0,
            "animal_events": [],
            "habitat_events": [],
            "random_event": None,
        }

        # 1) Animal daily ticks
        for animal in self.get_alive_animals():
            events = animal.daily_tick()
            summary["animal_events"].extend(events)

        # 2) Habitat / enclosure ticks
        for hab in self._habitats:
            events = hab.daily_tick()
            summary["habitat_events"].extend(events)

        # 3) Breeding checks
        for enc in self._enclosures:
            baby_msg = enc.check_breeding()
            if baby_msg:
                summary["events"].append(baby_msg)
                self._animals_born += 1

        # 4) Check for deaths
        death_events = self._check_deaths()
        summary["events"].extend(death_events)

        # 5) Visitors and revenue
        count, revenue = self._process_visitors()
        summary["visitors"] = count
        summary["revenue"] = revenue

        # 6) Welfare and finance checks → trigger observers
        self._check_welfare()
        self._check_finances()

        # 7) Random event
        rand_event = self._trigger_random_event()
        summary["random_event"] = rand_event

        # 8) Update score
        self._score = self._calculate_score()

        return summary

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _calculate_score(self) -> int:
        """
        Calculate the current player score.

        Score is based on average animal health, average visitor satisfaction,
        financial health, and number of unique species.

        Returns
        -------
        int
            Current score.
        """
        alive = self.get_alive_animals()
        if not alive:
            return 0

        avg_health = sum(a.health for a in alive) / len(alive)
        avg_happiness = sum(a.happiness for a in alive) / len(alive)

        avg_visitor_sat = 0.0
        if self._daily_visitors:
            avg_visitor_sat = (
                sum(v.satisfaction for v in self._daily_visitors)
                / len(self._daily_visitors)
            )

        unique_species = len({a.species for a in alive})
        balance = self._finance.get_balance()
        financial_score = min(100.0, (balance / 1000.0) * 10.0)

        score = int(
            avg_health * 0.35
            + avg_happiness * 0.25
            + avg_visitor_sat * 0.20
            + unique_species * 5
            + financial_score * 0.20
        )
        return score

    # ------------------------------------------------------------------
    # Status reporting
    # ------------------------------------------------------------------

    def get_status(self) -> str:
        """
        Return a formatted overview of the zoo's current status.

        Returns
        -------
        str
            Multi-line status string.
        """
        alive = self.get_alive_animals()
        avg_health = (sum(a.health for a in alive) / len(alive)) if alive else 0
        avg_happiness = (sum(a.happiness for a in alive) / len(alive)) if alive else 0
        balance = self._finance.get_balance()

        return (
            f"\n{'=' * 55}\n"
            f"  🦘 {self._name}  —  Day {self._day}\n"
            f"{'=' * 55}\n"
            f"  Balance      : ${balance:>12,.2f} AUD\n"
            f"  Ticket Price : ${self._ticket_price:>6.2f} AUD\n"
            f"  Total Visitors: {self._total_visitors:>6,}\n"
            f"  Animals (alive): {len(alive):>4}\n"
            f"  Avg Health   : {avg_health:>5.1f}/100\n"
            f"  Avg Happiness: {avg_happiness:>5.1f}/100\n"
            f"  Born (total) : {self._animals_born:>4}\n"
            f"  Died (total) : {self._animals_died:>4}\n"
            f"  Score        : {self._score:>6}\n"
            f"{'=' * 55}"
        )

    # ------------------------------------------------------------------
    # Save / Load helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise minimal zoo state to a plain dict for JSON save."""
        return {
            "name": self._name,
            "day": self._day,
            "ticket_price": self._ticket_price,
            "score": self._score,
            "total_visitors": self._total_visitors,
            "animals_born": self._animals_born,
            "animals_died": self._animals_died,
            "finance": self._finance.to_dict(),
            "food": self._food.to_dict(),
            "medicine": self._medicine.to_dict(),
        }

    def from_dict(self, data: dict) -> None:
        """
        Restore minimal zoo state from a plain dict (from JSON).

        Only the fields serialised by :meth:`to_dict` are restored.
        Animal and enclosure objects are *not* round-tripped — the zoo
        resets to its default starting state (same as a fresh ``__init__``)
        with statistics, finances, food, and medicine overwritten by the
        saved values.

        Parameters
        ----------
        data : dict
            Dictionary previously produced by :meth:`to_dict`.
        """
        self._day            = data.get("day", 0)
        self._ticket_price   = data.get("ticket_price", self.DEFAULT_TICKET_PRICE)
        self._score          = data.get("score", 0)
        self._total_visitors = data.get("total_visitors", 0)
        self._animals_born   = data.get("animals_born", 0)
        self._animals_died   = data.get("animals_died", 0)
        self._food.from_dict(data.get("food", {}))
        self._medicine.from_dict(data.get("medicine", {}))

    # ------------------------------------------------------------------
    # Accessors for CLI
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Zoo name."""
        return self._name

    @property
    def day(self) -> int:
        """Current simulation day."""
        return self._day

    @property
    def score(self) -> int:
        """Current player score."""
        return self._score

    @property
    def ticket_price(self) -> float:
        """Current ticket price in AUD."""
        return self._ticket_price

    @property
    def finance(self) -> Finance:
        """The Finance singleton."""
        return self._finance

    @property
    def food_inventory(self) -> FoodInventory:
        """The food inventory manager."""
        return self._food

    @property
    def medicine_inventory(self) -> MedicineInventory:
        """The medicine inventory manager."""
        return self._medicine

    @property
    def enclosures(self) -> List[Enclosure]:
        """All enclosures in the zoo."""
        return list(self._enclosures)

    @property
    def habitats(self) -> List[Habitat]:
        """All habitat zones in the zoo."""
        return list(self._habitats)

    @property
    def event_logger(self) -> EventLogger:
        """The event logger observer."""
        return self._event_logger

    @property
    def daily_visitors(self) -> List[Visitor]:
        """Visitors from the most recent day."""
        return list(self._daily_visitors)

    @property
    def total_visitors(self) -> int:
        """Cumulative visitor count across all days."""
        return self._total_visitors

    @property
    def animals_born(self) -> int:
        """Total animals born since the zoo opened."""
        return self._animals_born

    @property
    def animals_died(self) -> int:
        """Total animals that have died since the zoo opened."""
        return self._animals_died

    def __str__(self) -> str:
        alive = len(self.get_alive_animals())
        return (
            f"Zoo({self._name!r}, day={self._day}, "
            f"animals={alive}, score={self._score})"
        )

    def __repr__(self) -> str:
        return (
            f"Zoo(name={self._name!r}, day={self._day}, "
            f"animals={len(self._animals)}, "
            f"balance=${self._finance.get_balance():.2f})"
        )
