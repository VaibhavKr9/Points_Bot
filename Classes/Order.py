from datetime import datetime
from datetime import timedelta
from copy import deepcopy

from Errors import InvalidPositionException
from Errors import InvalidLengthException


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

    def updateFromList(self, orderList):
        for pos, driver in enumerate(orderList, start=1):
            try:
                self.update(pos, driver)
            except InvalidLengthException:
                raise InvalidLengthException

    def __str__(self):
        return str(" ".join(driver for driver in self.order_dict.values()))

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
    
    def driver(self, pos):
        return self.order_dict[pos]

    def orderList(self):
        return self.order_dict.values()

    def modifiedTime(self):
        return self.last_modified

    def modifiedTime_str(self):
        return (self.last_modified + timedelta(hours=5.5)).strftime("%d-%b-%y, %a, %H:%M")
