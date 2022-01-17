__author__ = 'fmy'

import collections
import random
import math


"数据模型"

# 一摞有序的纸牌
Card = collections.namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for rank in self.ranks
                       for suit in self.suits]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

    @property
    def cards(self):
        return self._cards


beer_card = Card('7', 'diamonds')
print(beer_card)

deck = FrenchDeck()
print(type(deck))
# __len__ 使得可以得到序列的长度
print(len(deck))
print(deck[-1])
print(deck[0])
# 随机从序列中抽取一张
print(random.choice(deck.cards))
print(random.choice(deck))
print(deck[:2])
print(deck[12:15:3])

# __getitem__方法使得一摞牌可迭代
# for card in deck:
#     print(card)
# for card in reversed(deck):
#     print(card)

suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)

# 一些验证
for card in deck[:2]:
    print(card.rank)
    print(FrenchDeck.ranks)
    print(FrenchDeck.ranks.index(card.rank))


# 定义排序函数
def spades_high(card):
    rank_value = FrenchDeck.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]


for card in sorted(deck, key=spades_high):
    print(card)


class Vector:

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        # 输出展示
        return 'Vector(%r, %r)' % (self.x, self.y)

    def __abs__(self):
        # 向量的模
        return math.hypot(self.x, self.y)

    def __bool__(self):
        # if判断
        return bool(abs(self))

    def __add__(self, other):
        # 向量加法
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x, y)

    def __mul__(self, scalar):
        # 标量乘法
        return Vector(self.x * scalar, self.y * scalar)


v1 = Vector(1, 2)
v2 = Vector(3, 1)
print(v1 + v2)
print(v1 * 5)
print(v1 * -5)
print(abs(v1))
print(Vector())
print(Vector)
print(math.hypot(5, 5, 5))
