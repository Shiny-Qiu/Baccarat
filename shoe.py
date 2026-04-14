import random
from card import Card


class Shoe:
    def __init__(self, num_decks: int = 8):
        self.num_decks = num_decks
        self.total_cards = num_decks * 52
        self.cards: list[Card] = []
        self.shuffle()

    def shuffle(self):
        self.cards = []
        for _ in range(self.num_decks):
            for suit in range(4):
                for rank in range(13):
                    self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)

    def deal_one(self) -> Card:
        if not self.cards:
            self.shuffle()
        return self.cards.pop()

    def needs_shuffle(self) -> bool:
        return len(self.cards) < 52

    @property
    def remaining(self) -> int:
        return len(self.cards)
