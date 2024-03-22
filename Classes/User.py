from Order import Order
from Countback import Countback
from Errors import InvalidLengthException
from Errors import InvalidPositionException


class User:
    def __init__(self):
        self.name: str = ""
        self.mention: str = ""
        self.points: int = 0
        self.weekPoints: int = 0
        self.weekWins: int = 0
        self.countback: Countback = Countback()
        self.gridPrediction: Order = Order()
        self.racePrediction: Order = Order()
        self.currPosition: int = 0
        self.prevPosition: int = 0

    def __str__(self) -> str:
        return self.name

    def incrementWins(self) -> None:
        self.weekWins = self.weekWins + 1

    def updateGridPred(self, QualiPred: Order) -> str:
        self.gridPrediction.updateFromOrder(QualiPred)
        msg = "✅ Quali prediction by" + self.name + \
            ": " + str(self.gridPrediction)
        return msg

    def updateRacePred(self, RacePred: Order) -> str:
        self.racePrediction.updateFromOrder(RacePred)
        msg = "✅ Race prediction by" + self.name + \
            ": " + str(self.racePrediction)
        return msg

    def updatePoints(self, gridResult: Order, raceResult: Order) -> None:
        self.weekPoints = 0
        for pos in range(start=1, stop=4):
            if gridResult.driver(pos) == self.gridPrediction.driver(pos):
                self.weekPoints = self.weekPoints + 1
            if gridResult.driver(pos) in self.gridPrediction.orderList():
                self.weekPoints = self.weekPoints + 1
            if raceResult.driver(pos) == self.racePrediction.driver(pos):
                self.weekPoints = self.weekPoints + 1
                self.countback.increment(pos)
            if raceResult.driver(pos) in self.racePrediction.orderList():
                self.weekPoints = self.weekPoints + 1
        self.points = self.points + self.weekPoints

    def __gt__(self, other) -> bool:
        if self.points != other.points:
            return self.points > other.points
        else:
            return self.countback > other.countback

    def __lt__(self, other) -> bool:
        if self.points != other.points:
            return self.points < other.points
        else:
            return self.countback < other.countback

    def __eq__(self, other) -> bool:
        return False

    def updatePosition(self, newPos: int) -> None:
        if newPos < 1:
            raise InvalidPositionException
        else:
            self.prevPosition = self.currPosition
            self.currPosition = newPos

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result