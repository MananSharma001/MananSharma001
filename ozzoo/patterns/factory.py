"""
patterns/factory.py
===================
Implements the **Factory** design pattern for creating Animal instances.

``AnimalFactory.create_animal(species_type, name, ...)`` centralises
construction logic so the rest of the codebase never needs to import
individual animal classes directly.

Supported species
-----------------
``"kangaroo"``, ``"koala"``, ``"penguin"``, ``"emu"``,
``"crocodile"``, ``"eagle"``, ``"snake"``
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from animals.animal import Animal


class AnimalFactory:
    """
    Factory class for creating Animal instances by species name.

    Usage
    -----
    >>> animal = AnimalFactory.create_animal("kangaroo", "Joey", age=2)
    """

    # Lazy import map to avoid circular imports at module load time
    _REGISTRY: dict[str, str] = {
        "kangaroo": "animals.marsupial.Kangaroo",
        "koala": "animals.marsupial.Koala",
        "penguin": "animals.flightless_bird.Penguin",
        "emu": "animals.flightless_bird.Emu",
        "crocodile": "animals.reptile.Crocodile",
        "snake": "animals.reptile.Snake",
        "eagle": "animals.bird.Eagle",
    }

    @classmethod
    def create_animal(
        cls,
        species_type: str,
        name: str,
        age: int = 1,
        **kwargs: Any,
    ) -> "Animal":
        """
        Instantiate and return an Animal of the requested species.

        Parameters
        ----------
        species_type : str
            Case-insensitive species key (see module docstring for valid values).
        name : str
            Name for the new animal.
        age : int
            Age of the animal in years.  Defaults to 1.
        **kwargs
            Additional keyword arguments forwarded to the animal constructor.

        Returns
        -------
        Animal
            A fully initialised Animal subclass instance.

        Raises
        ------
        ValueError
            If *species_type* is not recognised.
        """
        key = species_type.lower().strip()
        if key not in cls._REGISTRY:
            supported = ", ".join(sorted(cls._REGISTRY.keys()))
            raise ValueError(
                f"Unknown species '{species_type}'.  "
                f"Supported species: {supported}"
            )

        # Dynamic import to avoid top-level circular dependencies
        module_path, class_name = cls._REGISTRY[key].rsplit(".", 1)
        import importlib
        module = importlib.import_module(module_path)
        animal_class = getattr(module, class_name)
        return animal_class(name=name, age=age, **kwargs)

    @classmethod
    def supported_species(cls) -> list[str]:
        """
        Return a sorted list of supported species keys.

        Returns
        -------
        list[str]
            Lowercase species keys that can be passed to :meth:`create_animal`.
        """
        return sorted(cls._REGISTRY.keys())

    def __repr__(self) -> str:
        return f"AnimalFactory(supported={self.supported_species()})"
