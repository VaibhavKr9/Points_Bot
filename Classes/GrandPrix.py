from datetime import datetime
from copy import deepcopy

from Order import Order


class GrandPrix:
    def __init__(self):
        self.name: str = ""
        self.location: str = ""
        self.round: int = 0
        self.qualiTime: datetime = datetime.now()
        self.raceTime: datetime = datetime.now()
        self.gridResult: Order = Order()
        self.raceResult: Order = Order()

    def __str__(self):
        return self.name

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def qualiTime_str(self) -> str:
        return self.qualiTime.strftime("%a, %H:%M")

    def raceTime_str(self) -> str:
        return self.raceTime.strftime("%a, %H:%M")

    def raceDateTime_str(self) -> str:
        return self.raceTime.strftime("%d %B, %H:%M")

    def incrementRound(self) -> None:
        self.round = self.round + 1
