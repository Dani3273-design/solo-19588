import random
from itertools import permutations


SUITS = ['♠', '♥', '♦', '♣']
VALUES = list(range(1, 14))


class Card:
    def __init__(self, suit: str, value: int):
        self.suit = suit
        self.value = value

    def display_value(self) -> str:
        if self.value == 1:
            return 'A'
        elif self.value == 11:
            return 'J'
        elif self.value == 12:
            return 'Q'
        elif self.value == 13:
            return 'K'
        else:
            return str(self.value)

    def __str__(self) -> str:
        return f'{self.suit}{self.display_value()}'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash((self.suit, self.value))


def generate_deck() -> list[Card]:
    deck = []
    for suit in SUITS:
        for value in VALUES:
            deck.append(Card(suit, value))
    return deck


def can_make_24(nums: list[int]) -> bool:
    if len(nums) == 1:
        return abs(nums[0] - 24) < 1e-9

    for i in range(len(nums)):
        for j in range(len(nums)):
            if i == j:
                continue
            remaining = [nums[k] for k in range(len(nums)) if k != i and k != j]
            a, b = nums[i], nums[j]
            results = [a + b, a - b, a * b]
            if abs(b) > 1e-9:
                results.append(a / b)
            for val in results:
                if can_make_24(remaining + [val]):
                    return True
    return False


def is_solvable(card_values: list[int]) -> bool:
    for perm in permutations(card_values):
        if can_make_24(list(perm)):
            return True
    return False


def draw_unique_cards(count: int = 4) -> list[Card]:
    deck = generate_deck()
    random.shuffle(deck)
    cards = deck[:count]
    values = [c.value for c in cards]
    attempts = 0
    while not is_solvable(values) and attempts < 1000:
        random.shuffle(deck)
        cards = deck[:count]
        values = [c.value for c in cards]
        attempts += 1
    return cards
