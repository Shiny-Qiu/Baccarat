class Card:
    SUITS = ['\u2660', '\u2665', '\u2666', '\u2663']
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    def __init__(self, suit: int, rank: int):
        self.suit = suit   # 0=spade, 1=heart, 2=diamond, 3=club
        self.rank = rank   # 0=A, 1=2, ..., 8=9, 9=10, 10=J, 11=Q, 12=K

    @property
    def point(self) -> int:
        if self.rank >= 9:  # 10, J, Q, K
            return 0
        return self.rank + 1  # A=1, 2=2, ..., 9=9

    @property
    def suit_symbol(self) -> str:
        return self.SUITS[self.suit]

    @property
    def rank_str(self) -> str:
        return self.RANKS[self.rank]

    @property
    def is_red(self) -> bool:
        return self.suit in (1, 2)

    @property
    def color(self) -> str:
        return '#CC0000' if self.is_red else '#000000'

    def __repr__(self):
        return f"{self.suit_symbol}{self.rank_str}"
