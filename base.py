from datetime import datetime
from datetime import timedelta
import random


class InvalidLengthException(Exception):
    pass


class InvalidPositionException(Exception):
    pass


class Order:
    def __init__(self):
        self.order_dict = {
            1: "000",
            2: "000",
            3: "000"
        }
        self.last_modified = datetime.now()

    def update(self, pos, driver):
        if (pos > 0) and (pos < 4):
            if len(driver) == 3:
                self.order_dict[pos] = driver.upper()
                self.last_modified = datetime.now()
            else:
                raise InvalidLengthException
        else:
            raise InvalidPositionException

    def updateFromOrder(self, order):
        self.order_dict = order.order_dict
        self.last_modified = datetime.now()

    def __str__(self):
        return str(" ".join(driver for driver in self.order_dict.values()))

    def driver(self, pos):
        return self.order_dict[pos]

    def orderList(self):
        return self.order_dict.values()

    def modifiedTime(self):
        return self.last_modified

    def modifiedTime_str(self):
        return (self.last_modified + timedelta(hours=5.5)).strftime("%d-%b-%y, %a, %H:%M")


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
