"""
parrot.py
---------
Parrot – concrete animal class.

Inheritance chain:  Parrot → Bird → Animal (ABC)
"""

from ozzoo.animals.bird import Bird


class Parrot(Bird):
    """
    A macaw parrot: colourful, intelligent, and talkative.

    Inheritance chain:  Parrot → Bird → Animal

    Additional attributes
    ---------------------
    vocabulary : list[str] – words the parrot can repeat
    """

    _ticket_price: float = 12.0

    def __init__(self, name: str, vocabulary: list | None = None, **kwargs) -> None:
        super().__init__(name=name, species="Ara macao",
                         wingspan_cm=100.0, can_fly=True, **kwargs)
        self.vocabulary = vocabulary or ["hello", "pretty bird", "squawk"]

    def sound(self) -> str:
        return "SQUAWK"

    def diet(self) -> str:
        return "herbivore"

    def talk(self) -> str:
        """Parrot picks a random word from its vocabulary."""
        import random
        word = random.choice(self.vocabulary)
        self.happiness += 5
        return f'{self.name} says: "{word}"'

    def learn_word(self, word: str) -> str:
        """Teach the parrot a new word."""
        self.vocabulary.append(word)
        return f'{self.name} learned a new word: "{word}"'
