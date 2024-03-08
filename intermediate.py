from base import Order
from base import Countback
from base import InvalidLengthException
from base import InvalidPositionException
from datetime import datetime
from datetime import strftime


class User:
    def __init__(self):
        self.name = ""
        self.mention = ""
        self.points = 0
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

    def updatePoints(self, qualiResult, raceResult):
        for pos in range(start=1, stop=4):
            if qualiResult.driver(pos) == self.qualiPrediction.driver(pos):
                self.points = self.points + 1
            if qualiResult.driver(pos) in self.qualiPrediction.orderList():
                self.points = self.points + 1
            if raceResult.driver(pos) == self.racePrediction.driver(pos):
                self.points = self.points + 1
                self.countback.increment(pos)
            if raceResult.driver(pos) in self.racePrediction.orderList():
                self.points = self.points + 1

    def __gt__(self, other):
        if self.points != other.points:
            return self.points > other.points
        else:
            return self.countback > other.countback

    def updatePosition(self, newPos):
        if newPos < 1:
            raise InvalidPositionException
        else:
            self.prevPosition = self.currPosition
            self.currPosition = newPos


class GrandPrix:
    def __init__(self):
        self.name = ""
        self.location = ""
        self.round = 0
        self.qualiTime = datetime.now()
        self.raceTime = datetime.now()
        self.qualiResult = Order()
        self.raceResult = Order()

    def __str__(self):
        return self.name

    def qualiTime_str(self):
        return self.qualiTime.strftime("%a, %H:%M")

    def raceTime_str(self):
        return self.raceTime.strftime("%a, %H:%M")

    def raceDateTime_str(self):
        return self.raceTime.strftime("%d %B, %H:%M")

    def incrementRound(self):
        self.round = self.round + 1
