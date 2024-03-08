import random

from Errors import InvalidPositionException


class Countback:
    def __init__(self):
        self.__countback_dict = {
            1: 0,
            2: 0,
            3: 0
        }

    def increment(self, pos):
        if (pos > 0) and (pos < 4):
            self.__countback_dict[pos] = self.__countback_dict[pos] + 1
        else:
            raise InvalidPositionException

    def getCount(self, pos):
        return self.__countback_dict[pos]

    def __gt__(self, other):
        for pos in [1, 2, 3]:
            if self.__countback_dict[pos] != other.__countback_dict[pos]:
                return self.__countback_dict[pos] > other.__countback_dict[pos]
        return random.choice([True, False])

    def __str__(self):
        return str(", ".join(str(count) for count in self.__countback_dict.values()))
