from datetime import datetime
from copy import deepcopy
from enum import Enum
import pickle
import logging

from src.user_class.User import User
from src.grand_prix_class.GrandPrix import GrandPrix
from src.order_class.Order import Order
from src.errors_class.Errors import InvalidLengthException
from src.errors_class.Errors import InvalidPositionException

class OverrideState(Enum):
    NO_OVERRIDE = 1
    OPENED_BY_ADMIN = 2
    CLOSED_BY_ADMIN = 3

class Server:
    def __init__(self):
        self.guild: int = 0
        self.name: str = ""
        self.generalChannel: int = 0
        self.updatesChannel: int = 0
        self.adminOverrideFlag : OverrideState = OverrideState.NO_OVERRIDE
        self._playerDict: dict[int : User] = {}

    def newUser(self, id: int, name: str, mention: str) -> bool:
        if id not in self._playerDict.keys():
            user: User = User()
            user.id = id
            user.name = name
            user.mention = mention
            self._playerDict[id] = user
            logging.info("New user added: " + str(user))
            return True
        else:
            logging.info("Tried to add new user, but user already registered in the server: " + name)
            return False
        

    def _predUpdateUser(self, user : User, tag : str, order : Order) -> str:
        if tag == "race":
            logging.info(tag + " prediction update for " + str(user))
            return user.updateRacePred(order) + " for " + self.name
        elif tag == "grid":
            logging.info(tag + " prediction update for " + str(user))
            return user.updateGridPred(order) + " for " + self.name
        else:
            logging.error("Tag exception during prediction update.")
            return "Wrong tag used."

    def updatePredictions(self, tag: str, predList: list[str], userId : int = None, userName: str = None, userMention : str = None) -> str:
        """ if tag == "grid" and datetime.now() > self.currGrandPrix.qualiTime:
            return "❌ " + str(self.currGrandPrix) + " grid predictions are now closed."
        if tag == "race" and datetime.now() > self.currGrandPrix.raceTime:
            return "❌ " + str(self.currGrandPrix) + " race predictions are now closed." """
        order: Order = Order()
        try:
            for pos in range(3):
                order.update(pos, predList[pos])
        except InvalidLengthException:
            return "‼Enter three-letter abbreviations only."
        except InvalidPositionException:
            logging.error("Position exception during prediction update")
            return "A Position Exception occured."
        for user in self._playerDict:
            if userId != None and userId == user.id:
                return self._predUpdateUser(user, tag, order)
            elif userMention != None and userMention == user.mention:
                return self._predUpdateUser(user, tag, order)
            elif userName != None and userName == user.name:
                return self._predUpdateUser(user, tag, order)

        logging.info("User is not registered to update predictions")
        return "You don't seem to be registered in the server."

    """ def updateResults(self, gridResult: list[str], raceResult: list[str]) -> str:
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
                                               raceTimeStr[2]) """
        

    def updateStandings(self, gridResult: Order, raceResult: Order):
        newPositionList: list[User] = []
        userBackupList: list[User] = deepcopy(self._playerDict)

        for user in self._playerDict:
            user.updatePoints(gridResult, raceResult)

            insertedInListFlag = False
            if newPositionList:
                for pos, newPosUser in enumerate(newPositionList):
                    if user > newPosUser:
                        newPositionList.insert(pos,user)
                        insertedInListFlag = True
                        break
            if not insertedInListFlag:
                newPositionList.append(user)
        
        try:
            for user in self._playerDict:
                user.updatePosition(newPositionList.index(user) + 1)
            self._playerDict = newPositionList
        except InvalidPositionException:
            self._playerDict = userBackupList
            logging.error("Invalid position exception occured during standings update")

    def summary(self, grandPrix: GrandPrix) -> str:
        message: str = "The"
        message += grandPrix.name + " (Round " + str(grandPrix.round) + ") is over and here are the results:\n"
        message += "Grid: " + str(grandPrix.gridResult) + "\n"
        message += "Race: " + str(grandPrix.raceResult) + "\n"

        message += "\nGrid predictions:\n"
        message += "\n".join((str(user) + ": " + str(user.gridPredictions)) for user in self._playerDict)
        message += "\nRace Predictions:\n"
        message += "\n".join((str(user) + ": " + str(user.racePredictions)) for user in self._playerDict)

        message += "\nThe Championship Standings-\n"
        message += "`" + ": ^5".format("Pos") + " | "
        message += ": <30".format("Player") + " | "
        message += ": <6".format("Points") + " | "
        message += " Countback"

        #TODO: complete the summary

    def loadData(self, guildID: int) -> str:
        try:
            with open("pickles/" + str(guildID) + ".pickle", "rb") as pickleFile:
                self = pickle.load(pickleFile)
                logging.info("Server data loaded from pickle")
        except Exception as exception:
            logging.error("Server load from pickle failed due to exception: " + str(exception))
            raise exception
        
    def saveData(self) -> str:
        try:
            with open("pickles/" + str(self.guild) + ".pickle", "wb+") as pickleFile:
                pickle.dump(self, pickleFile, pickle.HIGHEST_PROTOCOL)
                logging.info("Server data saved to pickle")
        except Exception as exception:
            logging.error("Server save to pickle failed due to exception: " + str(exception))
            raise exception

