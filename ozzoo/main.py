"""
main.py
-------
OzZoo – entry-point demonstration script.

Run with:
    python -m ozzoo.main
or:
    python ozzoo/main.py
"""

from ozzoo.animals import Lion, Elephant, Eagle, Parrot, Crocodile, Gecko
from ozzoo.habitat import Habitat
from ozzoo.finance import Finance
from ozzoo.zoo import Zoo


def main() -> None:
    print("=" * 60)
    print("  Welcome to OzZoo – Object-Oriented Virtual Zoo Simulator")
    print("=" * 60)

    # ------------------------------------------------------------------ #
    #  1. Create the zoo                                                  #
    # ------------------------------------------------------------------ #
    zoo = Zoo(name="OzZoo", location="Sydney, Australia")
    print(f"\n✔  Zoo created: {zoo}\n")

    # ------------------------------------------------------------------ #
    #  2. Create habitats                                                 #
    # ------------------------------------------------------------------ #
    savannah = Habitat(
        name="African Savannah",
        climate="arid",
        enclosure_type="open",
        capacity=5,
        area_sqm=2000,
    )
    aviary = Habitat(
        name="Sky Aviary",
        climate="tropical",
        enclosure_type="aviary",
        capacity=8,
        area_sqm=800,
    )
    reptile_house = Habitat(
        name="Reptile House",
        climate="tropical",
        enclosure_type="terrarium",
        capacity=10,
        area_sqm=300,
    )

    print(zoo.add_habitat(savannah))
    print(zoo.add_habitat(aviary))
    print(zoo.add_habitat(reptile_house))

    # ------------------------------------------------------------------ #
    #  3. Create animals                                                  #
    # ------------------------------------------------------------------ #
    simba   = Lion(name="Simba", is_male=True, mane_length="long")
    nala    = Lion(name="Nala", is_male=False)
    dumbo   = Elephant(name="Dumbo", tusk_length_cm=180)
    freedom = Eagle(name="Freedom", altitude_m=4000)
    polly   = Parrot(name="Polly", vocabulary=["hello", "cracker", "OzZoo"])
    croc    = Crocodile(name="Snappy", length_m=5.2)
    leo     = Gecko(name="Leo")

    # ------------------------------------------------------------------ #
    #  4. Place animals into habitats                                     #
    # ------------------------------------------------------------------ #
    print("\n--- Placing animals into habitats ---")
    print(zoo.place_animal(simba,   "African Savannah"))
    print(zoo.place_animal(nala,    "African Savannah"))
    print(zoo.place_animal(dumbo,   "African Savannah"))
    print(zoo.place_animal(freedom, "Sky Aviary"))
    print(zoo.place_animal(polly,   "Sky Aviary"))
    print(zoo.place_animal(croc,    "Reptile House"))
    print(zoo.place_animal(leo,     "Reptile House"))

    # ------------------------------------------------------------------ #
    #  5. Interact with animals                                           #
    # ------------------------------------------------------------------ #
    print("\n--- Animal interactions ---")
    print(simba.sound())           # Lion roars
    print(simba.hunt())            # Lion-specific action
    print(dumbo.spray_water())     # Elephant-specific action
    print(freedom.fly())           # Bird method
    print(freedom.dive())          # Eagle-specific action
    print(polly.talk())            # Parrot-specific action
    print(polly.learn_word("OzZoo is cool!"))
    print(croc.bask(minutes=60))   # Reptile method
    print(croc.death_roll())       # Crocodile-specific action
    print(leo.climb_wall())        # Gecko-specific action
    print(simba.feed())            # Animal base method
    print(nala.play(duration_minutes=30))

    # ------------------------------------------------------------------ #
    #  6. Admit visitors & simulate a day                                 #
    # ------------------------------------------------------------------ #
    print("\n--- Admitting 100 visitors ---")
    for line in zoo.admit_visitors(count=100):
        print(line)

    print("\n--- Simulating one day ---")
    for line in zoo.simulate_day():
        print(line)

    # ------------------------------------------------------------------ #
    #  7. Full report                                                     #
    # ------------------------------------------------------------------ #
    print("\n")
    print(zoo.full_report())

    # ------------------------------------------------------------------ #
    #  8. Finance singleton demonstration                                 #
    # ------------------------------------------------------------------ #
    f1 = Finance()
    f2 = Finance()
    print(f"\n--- Finance singleton check ---")
    print(f"f1 is f2: {f1 is f2}")   # True – same object


if __name__ == "__main__":
    main()
