from datetime import datetime
from copy import deepcopy

from User import User
from GrandPrix import GrandPrix
from Order import Order
from Errors import InvalidLengthException
from Errors import InvalidPositionException


class Server:
    def __init__(self):
        self.guild: int = 0
        self.generalChannel: int = 0
        self.updatesChannel: int = 0
        self.players: list[User] = []
        self.prevGrandPrix: GrandPrix = GrandPrix()
        self.currGrandPrix: GrandPrix = GrandPrix()
        self.nextGrandPrix: GrandPrix = GrandPrix()

    def newUser(self, name: str, mention: str) -> None:
        user: User = User()
        user.name = name
        user.mention = mention
        self.players.append(user)

    def updatePredictions(self, tag: str, userName: str, predList: list[str]) -> str:
        if tag == "grid" and datetime.now() > self.currGrandPrix.qualiTime:
            return "❌ " + str(currGrandPrix) + " grid predictions are now closed."
        if tag == "race" and datetime.now() > self.currGrandPrix.raceTime:
            return "❌ " + str(currGrandPrix) + " race predictions are now closed."
        order: Order = Order()
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
                    return user.updateGridPred(order)
                else:
                    return "A Tag Exception occured."
        return "You don't seem to be registered in the server."

    def updateResults(self, gridResult: list[str], raceResult: list[str]) -> str:
        try:
            self.currGrandPrix.gridResult.updateFromList(gridResult)
            self.currGrandPrix.raceResult.updateFromList(raceResult)
        except InvalidLengthException:
            return "Something went wrong while updating results."

    def updateGrandPrix(self, name: str, location: str, round: int, qualiTimeStr: str, raceTimeStr:str) -> None:
        self.prevGrandPrix = deepcopy(self.currGrandPrix)
        self.currGrandPrix = deepcopy(self.nextGrandPrix)
        self.nextGrandPrix.name = name
        self.nextGrandPrix.location = location
        self.nextGrandPrix.round = round
        # change str to list
        self.nextGrandPrix.qualiTime = datetime(qualiTimeStr[0],
                                                qualiTimeStr[1],
                                                qualiTimeStr[2])
        self.nextGrandPrix.raceTime = datetime(raceTimeStr[0],
                                               raceTimeStr[1],
                                               raceTimeStr[2])

    def updateStandings(self):
        newPositionList: list[User] = []

        for user in self.players:
            user.updatePoints(self.currGrandPrix.gridResult,
                              self.currGrandPrix.raceResult)

            insertedInListFlag = False
            if newPositionList:
                for pos, newPosUser in enumerate(newPositionList):
                    if user > newPosUser:
                        newPositionList.insert(pos,user)
                        insertedInListFlag = True
                        break
            if not insertedInListFlag:
                newPositionList.append(user)
        
        userBackupList: list[User] = deepcopy(self.players)
        try:
            for user in self.players:
                user.updatePosition(newPositionList.index(user) + 1)
        except InvalidPositionException:
            self.players = userBackupList
            return "A Position Exception occured."

    def currentSummary(self, round: int) -> str:
        message: str = "The"
        message += self.currGrandPrix.name + " (Round " + str(self.currGrandPrix.round) + ") is over and here are the results:\n"
        message += "Grid: " + str(self.currGrandPrix.gridResult) + "\n"
        message += "Race: " + str(self.currGrandPrix.raceResult) + "\n"

        message += "\nGrid predictions:\n"
        message += "\n".join((str(user) + ": " + str(user.gridPredictions)) for user in self.players)
        message += "\nRace Predictions:\n"
        message += "\n".join((str(user) + ": " + str(user.racePredictions)) for user in self.players)

