import math
from dataclasses import dataclass, field

from card import Card
from shoe import Shoe


@dataclass
class RoundResult:
    player_cards: list[Card] = field(default_factory=list)
    banker_cards: list[Card] = field(default_factory=list)
    player_value: int = 0
    banker_value: int = 0
    is_natural: bool = False
    player_drew: bool = False
    banker_drew: bool = False
    winner: str = ''          # 'player', 'banker', 'tie'
    player_pair: bool = False
    banker_pair: bool = False
    total_cards: int = 0
    road_tags: list[str] = field(default_factory=list)
    new_shoe: bool = False


class BaccaratGame:
    def __init__(self, mode: str = 'traditional', num_decks: int = 8):
        self.shoe = Shoe(num_decks)
        self.num_decks = num_decks
        self.mode = mode  # 'traditional' or 'commission_free'
        self.history: list[RoundResult] = []

    @staticmethod
    def hand_value(cards: list[Card]) -> int:
        return sum(c.point for c in cards) % 10

    # ------------------------------------------------------------------ #
    #  Play one round (pre-compute all cards for animation)
    # ------------------------------------------------------------------ #
    def play_round(self) -> RoundResult:
        shuffled = False
        if self.shoe.needs_shuffle():
            self.shoe.shuffle()
            shuffled = True

        r = RoundResult()
        r.new_shoe = shuffled

        # Deal: P1, B1, P2, B2
        p1 = self.shoe.deal_one()
        b1 = self.shoe.deal_one()
        p2 = self.shoe.deal_one()
        b2 = self.shoe.deal_one()
        r.player_cards = [p1, p2]
        r.banker_cards = [b1, b2]

        r.player_pair = (p1.rank == p2.rank)
        r.banker_pair = (b1.rank == b2.rank)

        p_val = self.hand_value(r.player_cards)
        b_val = self.hand_value(r.banker_cards)

        # Natural check
        if p_val >= 8 or b_val >= 8:
            r.is_natural = True
        else:
            # --- Player drawing ---
            if p_val <= 5:
                p3 = self.shoe.deal_one()
                r.player_cards.append(p3)
                r.player_drew = True
                p3pt = p3.point

                # --- Banker drawing (player drew) ---
                if b_val <= 2:
                    r.banker_cards.append(self.shoe.deal_one())
                    r.banker_drew = True
                elif b_val == 3:
                    if p3pt != 8:
                        r.banker_cards.append(self.shoe.deal_one())
                        r.banker_drew = True
                elif b_val == 4:
                    if p3pt not in (0, 1, 8, 9):
                        r.banker_cards.append(self.shoe.deal_one())
                        r.banker_drew = True
                elif b_val == 5:
                    if p3pt not in (0, 1, 2, 3, 8, 9):
                        r.banker_cards.append(self.shoe.deal_one())
                        r.banker_drew = True
                elif b_val == 6:
                    if p3pt in (6, 7):
                        r.banker_cards.append(self.shoe.deal_one())
                        r.banker_drew = True
                # b_val == 7: stand
            else:
                # Player stands (6 or 7) -> banker draws if 0-5
                if b_val <= 5:
                    r.banker_cards.append(self.shoe.deal_one())
                    r.banker_drew = True

        # Final values
        r.player_value = self.hand_value(r.player_cards)
        r.banker_value = self.hand_value(r.banker_cards)
        r.total_cards = len(r.player_cards) + len(r.banker_cards)

        if r.player_value > r.banker_value:
            r.winner = 'player'
        elif r.banker_value > r.player_value:
            r.winner = 'banker'
        else:
            r.winner = 'tie'

        r.road_tags = self._build_road_tags(r)
        self.history.append(r)
        return r

    # ------------------------------------------------------------------ #
    #  Road tags  (outcome flags shown in road map)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _build_road_tags(r: RoundResult) -> list[str]:
        tags: list[str] = []
        if r.banker_pair:
            tags.append('\u5e84\u5bf9')
        if r.player_pair:
            tags.append('\u95f2\u5bf9')
        # Lucky 6
        if r.winner == 'banker' and r.banker_value == 6:
            if len(r.banker_cards) == 2:
                tags.append('\u5e78\u8fd06')
                tags.append('\u4e24\u724c\u5e78\u8fd06')
            else:
                tags.append('\u5e78\u8fd06')
                tags.append('\u4e09\u724c\u5e78\u8fd06')
        # Player Lucky 7
        if r.winner == 'player' and r.player_value == 7:
            if len(r.player_cards) == 2:
                tags.append('\u4e24\u724c\u95f2\u5e787')
            else:
                tags.append('\u4e09\u724c\u95f2\u5e787')
        # Super Lucky 7
        if r.winner == 'player' and r.player_value == 7 and r.banker_value == 6:
            tags.append(f'\u8d85\u5e787\u00b7{r.total_cards}\u724c')
        return tags

    # ------------------------------------------------------------------ #
    #  Settlement
    # ------------------------------------------------------------------ #
    def settle_bets(self, bets: dict[str, float], result: RoundResult) -> dict:
        """Return {bet_key: (net_profit, description)}
        net_profit > 0  => win
        net_profit == 0 => push
        net_profit < 0  => lose (always == -amount)
        """
        out = {}
        for key, amount in bets.items():
            if amount <= 0:
                continue
            out[key] = self._settle_one(key, amount, result)
        return out

    def _settle_one(self, key: str, amt: float, r: RoundResult):
        w = r.winner

        # ---------- Banker ----------
        if key == 'banker':
            if w == 'banker':
                if self.mode == 'traditional':
                    comm = math.ceil(amt * 0.05)
                    profit = amt - comm
                    return (profit, f"\u5e84\u8d62 1:1 \u6263\u4f63{comm} = +{profit:.0f}")
                else:
                    if r.banker_value == 6:
                        profit = amt * 0.5
                        return (profit, f"\u5e84\u4ee56\u70b9\u80dc 1:0.5 = +{profit:.0f}")
                    return (amt, f"\u5e84\u8d62 1:1 = +{amt:.0f}")
            if w == 'tie':
                return (0, "\u5e84 \u548c\u5c40\u9000\u6ce8")
            return (-amt, f"\u5e84\u8d1f -{amt:.0f}")

        # ---------- Player ----------
        if key == 'player':
            if w == 'player':
                return (amt, f"\u95f2\u8d62 1:1 = +{amt:.0f}")
            if w == 'tie':
                return (0, "\u95f2 \u548c\u5c40\u9000\u6ce8")
            return (-amt, f"\u95f2\u8d1f -{amt:.0f}")

        # ---------- Tie ----------
        if key == 'tie':
            if w == 'tie':
                p = amt * 8
                return (p, f"\u548c\u5c40 1:8 = +{p:.0f}")
            return (-amt, f"\u975e\u548c\u5c40 -{amt:.0f}")

        # ---------- Banker Pair ----------
        if key == 'banker_pair':
            if r.banker_pair:
                p = amt * 11
                return (p, f"\u5e84\u5bf9 1:11 = +{p:.0f}")
            return (-amt, f"\u65e0\u5e84\u5bf9 -{amt:.0f}")

        # ---------- Player Pair ----------
        if key == 'player_pair':
            if r.player_pair:
                p = amt * 11
                return (p, f"\u95f2\u5bf9 1:11 = +{p:.0f}")
            return (-amt, f"\u65e0\u95f2\u5bf9 -{amt:.0f}")

        # ---------- Lucky 6 (variable) ----------
        if key == 'lucky6':
            if w == 'banker' and r.banker_value == 6:
                if len(r.banker_cards) == 2:
                    p = amt * 12
                    return (p, f"\u5e78\u8fd06(\u4e24\u724c) 1:12 = +{p:.0f}")
                else:
                    p = amt * 20
                    return (p, f"\u5e78\u8fd06(\u4e09\u724c) 1:20 = +{p:.0f}")
            return (-amt, f"\u65e0\u5e78\u8fd06 -{amt:.0f}")

        # ---------- Two-card Lucky 6 ----------
        if key == 'lucky6_2card':
            if w == 'banker' and r.banker_value == 6 and len(r.banker_cards) == 2:
                p = amt * 22
                return (p, f"\u4e24\u724c\u5e78\u8fd06 1:22 = +{p:.0f}")
            return (-amt, f"\u975e\u4e24\u724c\u5e78\u8fd06 -{amt:.0f}")

        # ---------- Three-card Lucky 6 ----------
        if key == 'lucky6_3card':
            if w == 'banker' and r.banker_value == 6 and len(r.banker_cards) == 3:
                p = amt * 50
                return (p, f"\u4e09\u724c\u5e78\u8fd06 1:50 = +{p:.0f}")
            return (-amt, f"\u975e\u4e09\u724c\u5e78\u8fd06 -{amt:.0f}")

        # ---------- Super Lucky 7 (variable by total cards) ----------
        if key == 'super_lucky7':
            if w == 'player' and r.player_value == 7 and r.banker_value == 6:
                tc = r.total_cards
                if tc == 4:
                    p = amt * 30
                    return (p, f"\u8d85\u7ea7\u5e78\u8fd07(4\u724c) 1:30 = +{p:.0f}")
                if tc == 5:
                    p = amt * 40
                    return (p, f"\u8d85\u7ea7\u5e78\u8fd07(5\u724c) 1:40 = +{p:.0f}")
                if tc == 6:
                    p = amt * 100
                    return (p, f"\u8d85\u7ea7\u5e78\u8fd07(6\u724c) 1:100 = +{p:.0f}")
            return (-amt, f"\u975e\u8d85\u7ea7\u5e78\u8fd07 -{amt:.0f}")

        # ---------- Two-card Player Lucky 7 ----------
        if key == 'lucky7_2card':
            if w == 'player' and r.player_value == 7 and len(r.player_cards) == 2:
                p = amt * 6
                return (p, f"\u4e24\u724c\u95f2\u5e78\u8fd07 1:6 = +{p:.0f}")
            return (-amt, f"\u975e\u4e24\u724c\u95f2\u5e78\u8fd07 -{amt:.0f}")

        # ---------- Three-card Player Lucky 7 ----------
        if key == 'lucky7_3card':
            if w == 'player' and r.player_value == 7 and len(r.player_cards) == 3:
                p = amt * 15
                return (p, f"\u4e09\u724c\u95f2\u5e78\u8fd07 1:15 = +{p:.0f}")
            return (-amt, f"\u975e\u4e09\u724c\u95f2\u5e78\u8fd07 -{amt:.0f}")

        return (0, "")
