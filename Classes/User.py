from Order import Order
from Countback import Countback
from Errors import InvalidLengthException
from Errors import InvalidPositionException


class User:
    def __init__(self):
        self.name: str = ""
        self.mention: str = ""
        self.__points: int = 0
        self.__weekPoints: int = 0
        self.__weekWins: int = 0
        self.__countback: Countback = Countback()
        self.__weekCountback: Countback = Countback()
        self.gridPrediction: Order = Order()
        self.racePrediction: Order = Order()
        self.currPosition: int = 0
        self.prevPosition: int = 0

    def __str__(self) -> str:
        return self.name

    def incrementWins(self) -> None:
        self.__weekWins = self.__weekWins + 1

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
        self.__weekPoints = 0
        self.__weekCountback.clear()
        for pos in range(start=1, stop=4):
            if gridResult.driver(pos) == self.gridPrediction.driver(pos):
                self.__weekPoints = self.__weekPoints + 1
            if gridResult.driver(pos) in self.gridPrediction.orderList():
                self.__weekPoints = self.__weekPoints + 1
            if raceResult.driver(pos) == self.racePrediction.driver(pos):
                self.__weekPoints = self.__weekPoints + 1
                self.__weekCountback.increment(pos)
                self.__countback.increment(pos)
            if raceResult.driver(pos) in self.racePrediction.orderList():
                self.__weekPoints = self.__weekPoints + 1
        self.__points = self.__points + self.__weekPoints

    def __gt__(self, other) -> bool:
        if self.__points != other.__points:
            return self.__points > other.__points
        else:
            return self.__countback > other.__countback

    def __lt__(self, other) -> bool:
        if self.__points != other.__points:
            return self.__points < other.__points
        else:
            return self.__countback < other.__countback

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