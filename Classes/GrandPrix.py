from datetime import datetime
from copy import deepcopy

from Order import Order


class GrandPrix:
    def __init__(self):
        self.name = ""
        self.location = ""
        self.round = 0
        self.qualiTime = datetime.now()
        self.raceTime = datetime.now()
        self.gridResult = Order()
        self.raceResult = Order()

    def __str__(self):
        return self.name

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def qualiTime_str(self):
        return self.qualiTime.strftime("%a, %H:%M")

    def raceTime_str(self):
        return self.raceTime.strftime("%a, %H:%M")

    def raceDateTime_str(self):
        return self.raceTime.strftime("%d %B, %H:%M")

    def incrementRound(self):
        self.round = self.round + 1
