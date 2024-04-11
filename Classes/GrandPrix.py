from datetime import datetime
from copy import deepcopy

from Order import Order


class GrandPrix:
    """
    Class to store Grand Prix related data.

    Attributes
    ----------
    name: str
        Name of the GP
    location: str
        Location where the GP is taking place
    round: int
        Round number
    qualiTime: datetime
        Time when qualifying takes place
    raceTime: datetime
        Time when the GP race takes place
    gridResult: Order
        Top 3 on the starting grid
    raceResult: Order
        Top 3 in the finishing order
    """

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

    #TODO: IST offset
    def qualiTime_str(self) -> str:
        return self.qualiTime.strftime("%a, %H:%M")

    def raceTime_str(self) -> str:
        return self.raceTime.strftime("%a, %H:%M")

    def raceDateTime_str(self) -> str:
        return self.raceTime.strftime("%d %B, %H:%M")

    def incrementRound(self) -> None:
        self.round = self.round + 1
