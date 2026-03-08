"""Animal sub-package: base class and all concrete animal types."""

from ozzoo.animals.animal import Animal
from ozzoo.animals.mammal import Mammal
from ozzoo.animals.bird import Bird
from ozzoo.animals.reptile import Reptile
from ozzoo.animals.lion import Lion
from ozzoo.animals.elephant import Elephant
from ozzoo.animals.eagle import Eagle
from ozzoo.animals.parrot import Parrot
from ozzoo.animals.crocodile import Crocodile
from ozzoo.animals.gecko import Gecko

__all__ = [
    "Animal",
    "Mammal",
    "Bird",
    "Reptile",
    "Lion",
    "Elephant",
    "Eagle",
    "Parrot",
    "Crocodile",
    "Gecko",
]
