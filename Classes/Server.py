from datetime import datetime

from User import User
from GrandPrix import GrandPrix
from Order import Order
from Errors import InvalidLengthException
from Errors import InvalidPositionException


class Server:
    def __init__(self):
        self.guild = 0
        self.generalChannel = 0
        self.updatesChannel = 0
        self.players = []
        self.prevGrandPrix = GrandPrix()
        self.currGrandPrix = GrandPrix()
        self.nextGrandPrix = GrandPrix()

    def newUser(self, name, mention):
        user = User()
        user.name = name
        user.mention = mention
        self.players.append(user)

    def updatePredictions(self, tag, userName, predList):
        if tag == "grid" and datetime.now() > self.currGrandPrix.qualiTime:
            return "❌ " + str(currGrandPrix) + " grid predictions are now closed."
        if tag == "race" and datetime.now() > self.currGrandPrix.raceTime:
            return "❌ " + str(currGrandPrix) + " race predictions are now closed."
        order = Order()
        try:
            for pos in range(3):
                order.update(pos, predList[pos])
        except InvalidLengthException:
            return "‼Enter three-letter abbreviations only."
        except InvalidPositionException:
            return "A Position Exception occured."
        for user in self.players:
            if str(userName) == user:
                if tag == "race":
                    return user.updateRacePred(order)
                elif tag == "grid":
                    return user.updateQualiPred(order)
                else:
                    return "A Tag Exception occured."
        return "You don't seem to be registered in the server."

    self
     order = Order()
      for pos, driver in enumerate(RacePred, start=1):
           try:
                order.update(pos, driver)
            except InvalidPositionException:
                return "Something went wrong while updating predictions."
            except InvalidLengthException:
                return "Driver name must be a three-letter abbreviation."
