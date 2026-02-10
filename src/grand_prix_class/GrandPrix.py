from datetime import datetime, timedelta
from copy import deepcopy

from order_class.Order import Order
from errors_class.Errors import InvalidTagException


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
        self.startTime: datetime = datetime.now()
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
    
    def __eq__(self, other) -> bool:
        if(self.name != other.name):
            return False
        if(self.location != other.location): 
            return False
        if(self.round != other.round):
            return False
        
        return True

    #TODO: IST offset
    def qualiTime_str(self) -> str:
        return (self.qualiTime + timedelta(hours=5, minutes=30)).strftime("%a, %H:%M")

    def raceTime_str(self) -> str:
        return (self.raceTime + timedelta(hours=5, minutes=30)).strftime("%a, %H:%M")

    def raceDateTime_str(self) -> str:
        return (self.raceTime + timedelta(hours=5, minutes=30)).strftime("%d %B, %H:%M")

    def incrementRound(self) -> None:
        self.round = self.round + 1

    def predictionClosedMsg(self, tag : str) -> str:
        if tag == "grid":
            return "❌Grid Predictions for " + self.name + " are closed."
        elif tag == "race":
            return "❌Race Predictions for " + self.name + " are closed."
        else:
            raise InvalidTagException