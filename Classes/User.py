from Order import Order
from Countback import Countback
from Errors import InvalidLengthException
from Errors import InvalidPositionException


class User:
    def __init__(self):
        self.name = ""
        self.mention = ""
        self.points = 0
        self.weekPoints = 0
        self.weekWins = 0
        self.countback = Countback()
        self.qualiPrediction = Order()
        self.racePrediction = Order()
        self.currPosition = 0
        self.prevPosition = 0

    def __str__(self):
        return self.name

    def incrementWins(self):
        self.weekWins = self.weekWins + 1

    def updateQualiPred(self, QualiPred):
        self.qualiPrediction.updateFromOrder(QualiPred)
        msg = "✅ Quali prediction by" + self.name + \
            ": " + str(self.qualiPrediction)
        return msg

    def updateRacePred(self, RacePred):
        self.racePrediction.updateFromOrder(RacePred)
        msg = "✅ Race prediction by" + self.name + \
            ": " + str(self.racePrediction)
        return msg

    def updatePoints(self, gridResult, raceResult):
        self.weekPoints = 0
        for pos in range(start=1, stop=4):
            if gridResult.driver(pos) == self.qualiPrediction.driver(pos):
                self.weekPoints = self.weekPoints + 1
            if gridResult.driver(pos) in self.qualiPrediction.orderList():
                self.weekPoints = self.weekPoints + 1
            if raceResult.driver(pos) == self.racePrediction.driver(pos):
                self.weekPoints = self.weekPoints + 1
                self.countback.increment(pos)
            if raceResult.driver(pos) in self.racePrediction.orderList():
                self.weekPoints = self.weekPoints + 1
        self.points = self.points + self.weekPoints

    def __gt__(self, other):
        if self.points != other.points:
            return self.points > other.points
        else:
            return self.countback > other.countback

    def __lt__(self, other):
        if self.points != other.points:
            return self.points < other.points
        else:
            return self.countback < other.countback

    def __eq__(self, other):
        return False

    def updatePosition(self, newPos):
        if newPos < 1:
            raise InvalidPositionException
        else:
            self.prevPosition = self.currPosition
            self.currPosition = newPos
