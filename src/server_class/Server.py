from datetime import datetime
from copy import deepcopy
from enum import Enum
import os
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
    def __init__(self, name : str = "", guildID : int = 0):
        self.__logger = logging.getLogger(str(guildID))
        self.__fileHandler = logging.FileHandler(f"{os.getenv("LOG_DIR")}/{guildID}.log")
        self.__fileHandler.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(self.__fileHandler)
        self.__pickleFilePath = f"{os.getenv("PICKLE_DIR")}/{guildID}.pickle"

        self.guildID: int = guildID
        self.name: str = name
        self.adminChannel: int = 0
        self.updatesChannel: int = 0
        self.adminOverrideFlag : OverrideState = OverrideState.NO_OVERRIDE
        self.passivePredictionActive : bool = True
        self.autoUpdatesActive : bool = True
        self.__playerDict: dict[int, User] = {}
        self.__weekendPosList : list[int] = []
        self.__weekendWinnerList : list[int] = []
        self.__ChampionshipPosList : list[int] = []

        if os.path.isfile(self.__pickleFilePath):
            self.__loadData()
            self.__logger.info(f"Server: {self.name} - Client initializing server from pickle file.")
        else:
            self.__saveData()
            self.__logger.info(f"Server: {self.name} - New server created.")

    def newUser(self, id: int, name: str, mention: str) -> bool:
        if id not in self.__playerDict.keys():
            user: User = User()
            user.id = id
            user.name = name
            user.mention = mention
            self.__playerDict[id] = user
            self.__saveData()
            self.__logger.info(f"Server: {self.name} - New user added: {user}")
            return True
        else:
            self.__logger.info(f"Server: {self.name} - Tried to add new user, but user already registered in the server: {name}")
            return False
        
    def removeUser(self, name: str | None = None, mention: str | None = None) -> bool:
        for userID, user in self.__playerDict.items():
            if (name != None and user.name == name) or (mention != None and user.mention == mention):
                del self.__playerDict[userID]
                self.__saveData()
                self.__logger.info(f"Server: {self.name} - User removed: {user}")
                return True
        self.__logger.info(f"Server: {self.name} - Tried to remove user, but user not found in the server: {name if name != None else "None"}")
        return False
        

    def _predUpdateUser(self, user : User, tag : str, order : Order) -> str:
        if tag == "race":
            self.__logger.info(f"Server: {self.name} - {tag} prediction update for {user}")
            return user.updateRacePred(order) + "\nFor " + self.name
        elif tag == "grid":
            self.__logger.info(f"Server: {self.name} - {tag} prediction update for {user}")
            return user.updateGridPred(order) + "\nFor " + self.name
        else:
            self.__logger.error(f"Server: {self.name} - Tag exception during prediction update.")
            return "Wrong tag used."

    def updatePredictions(self, tag: str, predList: list[str], userId : int | None = None, userName: str |None = None, userMention : str | None = None) -> str:

        order: Order = Order()
        try:
            for pos in range(1,4):
                order.update(pos, predList[pos])
        except InvalidLengthException:
            return "‼Enter three-letter abbreviations only."
        except InvalidPositionException:
            self.__logger.error(f"Server: {self.name} - Position exception during prediction update")
            return "A Position Exception occured."
        except Exception as exp:
            self.__logger.exception(f"Server: {self.name} - Exception during prediction update: {str(exp)}")
        message : str = ""
        for user in self.__playerDict.values():
            if userId != None and userId == user.id:
                message = self._predUpdateUser(user, tag, order)
                self.__saveData()
                return message
            elif userMention != None and userMention == user.mention:
                message = self._predUpdateUser(user, tag, order)
                self.__saveData()
                return message
            elif userName != None and userName == user.name:
                message = self._predUpdateUser(user, tag, order)
                self.__saveData()
                return message

        self.__logger.info(f"Server: {self.name} - User is not registered to update predictions: {userName if userName != None else "None"}")
        return "You don't seem to be registered in the server."
        

    def updateStandings(self, gridResult: Order, raceResult: Order) -> bool:
        try:
            self.__weekendPosList = []
            self.__ChampionshipPosList = []
            self.__weekendWinnerList = []
            backupPosList : list[int] = deepcopy(self.__ChampionshipPosList)
            maxWeekendPoints : int = -1

            for user in self.__playerDict.values():
                user.updatePoints(gridResult, raceResult)

                insertedInListFlag = False
                if self.__weekendPosList != []:
                    for pos, newPosUserID in enumerate(self.__weekendPosList):
                        if user.greaterWeekendThan(self.__playerDict[newPosUserID]):
                            self.__weekendPosList.insert(pos, user.id)
                            insertedInListFlag = True
                            break
                if not insertedInListFlag:
                    self.__weekendPosList.append(user.id)

                if self.__weekendWinnerList != []:
                    if user.greaterWeekendThan(self.__playerDict[self.__weekendWinnerList[0]]):
                        self.__weekendWinnerList = [user.id]
                    elif user.equalWeekendTo(self.__playerDict[self.__weekendWinnerList[0]]):
                        self.__weekendWinnerList.append(user.id)
                else:
                    self.__weekendWinnerList.append(user.id)
                
                insertedInListFlag = False
                if self.__ChampionshipPosList != []:
                    for pos, newPosUserID in enumerate(self.__ChampionshipPosList):
                        if user > self.__playerDict[newPosUserID]:
                            self.__ChampionshipPosList.insert(pos, user.id)
                            insertedInListFlag = True
                            break
                if not insertedInListFlag:
                    self.__ChampionshipPosList.append(user.id)
            
            for user in self.__playerDict.values():
                user.updatePosition(self.__ChampionshipPosList.index(user.id) + 1)
            self.__saveData()
            return True
        
        except InvalidPositionException:
            self.__loadData()
            self.__logger.error(f"Server: {self.name} - Invalid position exception occured during standings update")
            return False
        except Exception as exception:
            self.__loadData()
            self.__logger.exception(f"Server: {self.name} - Exception occured during standings update: {str(exception)}")
            return False

    def manualUpdatePoints(self, newPoints : int, userName : str|None = None, userMention : str|None = None) -> str:
        for user in self.__playerDict.values():
            if userName is not None and user.name == userName:
                return user.manualUpdatePoints(newPoints)
            elif userMention is not None and user.mention == userMention:
                return user.manualUpdatePoints(newPoints)
            
        return "The user is not registered on the server."

    def manualUpdateCountback(self, newCountback : list[int], userName : str|None = None, userMention : str|None = None) -> str:
        for user in self.__playerDict.values():
            if userName is not None and user.name == userName:
                return user.manualUpdateCountback(newCountback)
            elif userMention is not None and user.mention == userMention:
                return user.manualUpdateCountback(newCountback)
            
        return "The user is not registered on the server."

    def clearActivePredictions(self) -> None:
        if not self.passivePredictionActive:
            for user in self.__playerDict.values():
                user.resetPredictions()
        
        self.__saveData()

    def isUserRegistered(self, userId: int) -> bool:
        return True if userId in self.__playerDict.keys() else False

    def weekendSummary(self) -> str:
        message : str = "**Predictions Summary:**\n"
        message +=      "\nGrid predictions:\n"
        message +=      "\n".join((str(user) + ": " + str(user.gridPrediction)) for user in self.__playerDict.values())
        message +=      "\nRace Predictions:\n"
        message +=      "\n".join((str(user) + ": " + str(user.racePrediction)) for user in self.__playerDict.values())

        message +=      "\n\n**Weekend Summary:**\n"
        message +=      "`" + ": ^5".format("Pos") + " | "
        message +=      ": <30".format("Player") + " | "
        message +=      ": <6".format("Points") + " | "
        message +=      " Countback\n"
        message +=      "\n".join(self.__playerDict[userID].weekSummary() for userID in self.__weekendPosList)
        message +=      "\nWeekend Winner(s):" + " ".join(self.__playerDict[userID].mention for userID in self.__weekendWinnerList)

        message += "\n\n**The Championship Standings-**\n"
        message += "`" + ": ^5".format("Pos") + " | "
        message += ": <30".format("Player") + " | "
        message += ": <6".format("Points") + " | "
        message += " Countback"
        message += "\n".join(self.__playerDict[userID].summary() for userID in self.__ChampionshipPosList)

        return message
    
    def championshipSummary(self) -> str:
        message : str = ""
        if len(self.__playerDict) > 0:
            message += "🥇" + self.__playerDict[self.__ChampionshipPosList[0]].mention + "\n"
        if len(self.__playerDict) > 1:
            message += "🥈" + self.__playerDict[self.__ChampionshipPosList[1]].mention + "\n"
        if len(self.__playerDict) > 2:
            message += "🥉" + self.__playerDict[self.__ChampionshipPosList[2]].mention + "\n"
        if len(self.__playerDict) > 0:
            message += "\n**Our " + str(datetime.now().year) + " Champion:** 👑" + self.__playerDict[self.__ChampionshipPosList[0]].mention + "\n"
            message += "Congratulations!!\n"

    def __loadData(self) -> None:
        try:
            with open(self.__pickleFilePath, "rb") as pickleFile:
                serverInfo = pickle.load(pickleFile)
                self.guildID =                  serverInfo["guildID"]
                self.name =                     serverInfo["name"]
                self.adminChannel =             serverInfo["adminChannel"]
                self.updatesChannel =           serverInfo["updatesChannel"]
                self.adminOverrideFlag =        serverInfo["adminOverrideFlag"]
                self.passivePredictionActive =  serverInfo["passivePredictionActive"]
                self.autoUpdatesActive =        serverInfo["autoUpdatesActive"]
                self.__playerDict =             serverInfo["playerDict"]
                self.__weekendPosList =         serverInfo["weekendPosList"]
                self.__weekendWinnerList =      serverInfo["weekendWinnerList"]
                self.__ChampionshipPosList =    serverInfo["ChampionshipPosList"]

                self.__logger.info(f"Server: {self.name} - Server data loaded from pickle")
        except Exception as exception:
            self.__logger.exception(f"Server: {self.name} - Server load from pickle failed due to exception: {str(exception)}")
            raise exception
        
    def __saveData(self) -> None:
        try:
            with open(self.__pickleFilePath, "wb+") as pickleFile:
                serverInfo = {
                    "guildID" :                     self.guildID,
                    "name" :                        self.name,
                    "adminChannel" :                self.adminChannel,
                    "updatesChannel" :              self.updatesChannel,
                    "adminOverrideFlag" :           self.adminOverrideFlag,
                    "passivePredictionActive" :     self.passivePredictionActive,
                    "autoUpdatesActive" :           self.autoUpdatesActive,
                    "playerDict" :                  self.__playerDict,
                    "weekendPosList" :              self.__weekendPosList,
                    "weekendWinnerList" :           self.__weekendWinnerList,
                    "ChampionshipPosList" :         self.__ChampionshipPosList
                }
                pickle.dump(serverInfo, pickleFile, pickle.HIGHEST_PROTOCOL)
                self.__logger.info(f"Server: {self.name} - Server data saved to pickle")
        except Exception as exception:
            self.__logger.exception(f"Server: {self.name} - Server save to pickle failed due to exception: {str(exception)}")
            raise exception

