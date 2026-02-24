import discord
import logging
from os import path
import pickle
from datetime import datetime
from copy import deepcopy
from server_class.Server import Server
from server_class.Server import OverrideState
from grand_prix_class.GrandPrix import GrandPrix
import errors_class.Errors as err

USER_COMMANDS = ["!predict", "!add me", "!remove me"]
ADMIN_COMMANDS = ["!change", "!add", "!remove", "!open", "!close", "!auto", "!admin channel", "!updates channel", "!disable passive", "!enable passive", "!pause", "!resume"]



class   DiscordClient(discord.Client):
    def __init__(self):
        self.__logger : logging.Logger = logging.getLogger('DiscordClient')
        self.__logger.setLevel(logging.DEBUG)
        self.__intents = discord.Intents(value = 0, messages = True, guilds = True, members = True, message_content = True)
        super().__init__(intents= self.__intents)
        self.__pickleFilePath : str = "clientData.pkl"
        self.__guildDict : dict[int, Server] = {}
        self.__guildUpdateStatusDict : dict[int, bool] = {}
        self.__isActive : bool = False
        self.__adminOverrideActive : bool = False
        self.currGrandPrix : GrandPrix = GrandPrix()
        self.nextGrandPrix : GrandPrix = GrandPrix()
        self.totalRounds : int = 0

    def startClient(self, authKey : str, pickleFilePath : str, logPath : str = "client.log") -> None:
        try:
            self.__logHandler : logging.Handler = logging.FileHandler(filename=logPath, encoding="utf-8")
            self.__logHandler.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            self.__logger.addHandler(self.__logHandler)
            self.__logger.info("Starting Discord Client...")
            self.run(token= authKey, reconnect= True, log_handler= self.__logHandler)
            #await self.wait_until_ready()

            if path.isfile(pickleFilePath):
                self.__pickleFilePath = pickleFilePath
                with open(pickleFilePath, "rb") as pickleFile:
                    self.__logger.info("Pickle file found, loading saved data...")
                    clientInfo = pickle.load(pickleFile)
                    self.currGrandPrix              = clientInfo["currGrandPrix"]
                    self.nextGrandPrix              = clientInfo["nextGrandPrix"]
                    self.totalRounds                = clientInfo["totalRounds"]
                    self.__adminOverrideActive      = clientInfo["adminOvrdAct"]
                    self.__guildUpdateStatusDict    = clientInfo["gldUpdateSts"]
                    for guildID in clientInfo["guildIDList"]:
                        guild = Server(guildID=guildID)
                        self.__guildDict[guildID] = guild
                    self.__isActive = True
                    self.__logger.info("Client is active.")
            else:
                self.__pickleFilePath = pickleFilePath
                for guild in self.guilds:
                    server : Server = Server(guild.name, guild.id)
                    self.__guildDict[guild.id] = server
                    self.__guildUpdateStatusDict[guild.id] = False
                self.__saveData()
                self.__isActive = True
                self.__logger.warning("Pickle file not found, client started with initailized data.")

        except Exception as exception:
            print("Error in starting the client: ", exception)

    def __saveData(self) -> None:
        if self.__isActive:
            with open(self.__pickleFilePath, "wb+") as pickleFile:
                clientInfo = {"guildIDList"  : list(self.__guildDict.keys()),
                              "adminOvrdAct" : self.__adminOverrideActive,
                              "gldUpdateSts" : self.__guildUpdateStatusDict,
                              "currGrandPrix": self.currGrandPrix,
                              "nextGrandPrix": self.nextGrandPrix,
                              "totalRounds"  : self.totalRounds}
                pickle.dump(clientInfo, pickleFile, pickle.HIGHEST_PROTOCOL)
                self.__logger.debug("Client data written to pickle file.")

    def isPredictionUpdateAllowed(self, tag : str) -> bool:
        if datetime.now() < self.currGrandPrix.startTime:
            return False
        if tag == "grid":
            if self.currGrandPrix.qualiTime > datetime.now():
                return True
            else:
                return False
        elif tag == "race":
            if self.currGrandPrix.raceTime > datetime.now():
                return True
            else:
                return False
        else:
            raise err.InvalidTagException
        
    def moveToNextGrandPrix(self) -> None:
        self.currGrandPrix = deepcopy(self.nextGrandPrix)
        self.__saveData()

    def updateNextGrandPrix(self, grandPrix : GrandPrix, totalRounds : int) -> None:
        self.nextGrandPrix = deepcopy(grandPrix)
        self.totalRounds = totalRounds
        self.__logger.info(f"Updated- Next Grand Prix: {self.nextGrandPrix} ; Total Rounds: {self.totalRounds}")
        self.__saveData()

    def areAllServersUpdated(self) -> bool:
        for status in self.__guildUpdateStatusDict.values():
            if not status:
                return False
        return True
            
    async def _easterEggs(self, message : discord.Message):
        pass

        #TODO: Easter eggs

    async def __userCommandHandler(self, message : discord.Message):
        if message.content.startswith("!predict"):
            predList : list[str] = []
            userFound : bool = False
            [com, tag, predList[0], predList[1], predList[2]] = message.content.lower().split(" ")
            try:
                if self.__adminOverrideActive or self.isPredictionUpdateAllowed(tag):
                    for guild in self.__guildDict.values():
                        if guild.isUserRegistered(message.author.id):
                            userFound = True
                            if (((guild.adminOverrideFlag == OverrideState.NO_OVERRIDE) and (self.isPredictionUpdateAllowed(tag))) or\
                                (guild.adminOverrideFlag == OverrideState.OPENED_BY_ADMIN)):
                                await message.channel.send(guild.updatePredictions(tag, predList, userName = message.author.name))
                            else:
                                await message.channel.send(self.currGrandPrix.predictionClosedMsg(tag) + " for " + guild.name)
                    if not userFound:
                        await message.channel.send("You don't seem to be registered on any server.")
                else:
                    await message.channel.send(self.currGrandPrix.predictionClosedMsg(tag))
            except err.InvalidTagException:
                await message.channel.send("To predict: !predict <grid/race> <P1> <P2> <P3>")

        elif message.content.lower() == "!add me":
            if message.guild:
                if self.__guildDict[message.guild.id].newUser(message.author.id, message.author.name, message.author.mention):
                    await message.channel.send("👋Welcome to the championship "+ message.author.mention + "!")
                else:
                    await message.channel.send("You are already registered in this server")
            else:
                await message.channel.send("Send this message on a channel of the server you want to take part in the championship of")

        elif message.content.lower() == "!remove me":
            if message.guild:
                if self.__guildDict[message.guild.id].removeUser(name = message.author.name):
                    await message.channel.send("You have been removed from the championship, " + message.author.mention + ". Thanks for playing!")
                else:
                    await message.channel.send("You are not registered in this server.")
            else:
                await message.channel.send("Send this message on a channel of the server you want to be removed from the championship of")

    async def __adminCommandHandler(self, message : discord.Message):
        if message.guild != None and (message.author.guild_permissions.administrator == True or message.channel.id == self.__guildDict[message.guild.id].adminChannel):
            if message.content.startswith("!change grid") or message.content.startswith("!change race"):
                predList : list[str] = []
                userFound : bool = False
                [com, tag, mention, predList[0], predList[1], predList[2]] = message.content.lower().split(" ")
                await message.channel.send(self.__guildDict[message.guild.id].updatePredictions(tag, predList, userMention = mention))

            if message.content.startswith("!change points"):
                [com, p, mention, newPoints] = message.content.lower().split(" ")
                await message.channel.send(self.__guildDict[message.guild.id].manualUpdatePoints(int(newPoints), userMention = mention))

            #TODO: change countback

            elif message.content.startswith("!add"):
                [com, mention] = message.content.split(" ")
                async for member in message.guild.fetch_members():
                    if member.mention == mention:
                        if self.__guildDict[message.guild.id].newUser(member.id, member.name, member.mention):
                            await message.channel.send("👋Welcome to the championship "+ member.mention + "!")
                        else:
                            await message.channel.send(member.name + " is already registered on the server.")

            elif message.content.startswith("!remove"):
                [com, mention] = message.content.split(" ")
                if self.__guildDict[message.guild.id].removeUser(mention = mention):
                    await message.channel.send(mention + " has been removed from the championship.")
                else:
                    await message.channel.send(mention + " is not registered on the server.")

            elif message.content.lower() == "!open":
                self.__guildDict[message.guild.id].adminOverrideFlag = OverrideState.OPENED_BY_ADMIN
                self.__adminOverrideActive = True
            
            elif message.content.lower() == "!close":
                self.__guildDict[message.guild.id].adminOverrideFlag = OverrideState.CLOSED_BY_ADMIN
                self.__adminOverrideActive = True

            elif message.content.lower() == "!auto":
                self.__guildDict[message.guild.id].adminOverrideFlag = OverrideState.NO_OVERRIDE
                self.__adminOverrideActive = False
                for guild in self.__guildDict.values():
                    if guild.adminOverrideFlag != OverrideState.NO_OVERRIDE:
                        self.__adminOverrideActive = True
                        break

            elif message.content.lower() == "!admin channel":
                self.__guildDict[message.guild.id].adminChannel = message.channel.id
                await message.channel.send("This channel has been set as the admin channel for the server.")

            elif message.content.lower() == "!updates channel":
                self.__guildDict[message.guild.id].updatesChannel = message.channel.id
                await message.channel.send("This channel has been set as the updates channel for the server.")

            elif message.content.lower() == "!disable passive":
                self.__guildDict[message.guild.id].passivePredictionActive = False
                await message.channel.send("Passive predictions have been disabled for the server.")

            elif message.content.lower() == "!enable passive":
                self.__guildDict[message.guild.id].passivePredictionActive = True
                await message.channel.send("Passive predictions have been enabled for the server.")

            elif message.content.lower() == "!pause":
                self.__guildDict[message.guild.id].autoUpdatesActive = False
                await message.channel.send("Auto updates have been paused for the server.")

            elif message.content.lower() == "!resume":
                self.__guildDict[message.guild.id].autoUpdatesActive = True
                await message.channel.send("Auto updates have been resumed for the server.")

            self.__saveData()
        
        else:
            await message.channel.send("You don't have the required permissions to run admin commands.")

    async def sendSchedule(self):
        commonMessageText : str = "🟢The predictions for " + str(datetime.now().year) + " " + str(self.currGrandPrix) + " are now open!\n\n"
        commonMessageText +=      "They will close at the start of each session at the following times-\n"
        commonMessageText +=      "Qualifying: " + self.currGrandPrix.qualiTime_str() + "\n"
        commonMessageText +=      "Race: " + self.currGrandPrix.raceTime_str()

        for guild in self.__guildDict.values():
            if guild.autoUpdatesActive:
                channel = self.get_channel(guild.updatesChannel)
                guildMessageText : str = ""

                if not guild.passivePredictionActive:
                    guild.clearActivePredictions()
                    guildMessageText = "\n\n**Note**: Passive predictions are disabled on this server. Previous predictions have been cleared."

                if type(channel) == discord.TextChannel:
                    await channel.send(commonMessageText + guildMessageText)
            self.__guildUpdateStatusDict[guild.guildID] = False
        self.__saveData()

    async def closePredictions(self, tag : str):
        commonMessageText : str = ""
        if tag == "grid" and self.currGrandPrix.qualiTime <= datetime.now():
            commonMessageText = "🟡The grid predictions for " + str(self.currGrandPrix) + " are now closed."
        elif tag == "race" and self.currGrandPrix.raceTime <= datetime.now():
            commonMessageText = "🔴The race predictions for " + str(self.currGrandPrix) + " are now closed."

        for guild in self.__guildDict.values():
            if guild.autoUpdatesActive:
                channel = self.get_channel(guild.updatesChannel)
                if type(channel) == discord.TextChannel:
                    await channel.send(commonMessageText)

    async def updateResults(self, gridResultList : list[str], raceResultList : list[str]) -> None:
        self.currGrandPrix.gridResult.updateFromList(gridResultList)
        self.currGrandPrix.raceResult.updateFromList(raceResultList)

        commonMessageText : str =   "🏁The  " + str(self.currGrandPrix.startTime.year) + " " + str(self.currGrandPrix) +\
                         " (Round " + str(self.currGrandPrix.round) + "/" + str(self.totalRounds) + ") in " + self.currGrandPrix.location +\
                         " is over and here are the results!\n\n"
        commonMessageText +=        "**Starting Grid:** " + str(self.currGrandPrix.gridResult) + "\n"
        commonMessageText +=        "**Race Results:** " + str(self.currGrandPrix.raceResult) + "\n\n"

        bottomMessageText : str = ""
        if self.nextGrandPrix.startTime.year == self.currGrandPrix.startTime.year and self.nextGrandPrix.round == self.currGrandPrix.round + 1:
            bottomMessageText = "\n\n🔔See you next at the " + str(self.nextGrandPrix) + "(Round " +str(self.nextGrandPrix.round) + ") in " +\
                         self.nextGrandPrix.location + " on " + self.nextGrandPrix.raceDateTime_str() + "!"
        
        for guild in self.__guildDict.values():
            if guild.autoUpdatesActive and not self.__guildUpdateStatusDict[guild.guildID]:
                self.__guildUpdateStatusDict[guild.guildID] = guild.updateStandings(self.currGrandPrix.gridResult, self.currGrandPrix.raceResult)
                guildSummaryText : str = guild.weekendSummary()
                channel = self.get_channel(guild.updatesChannel)
                if type(channel) == discord.TextChannel:
                    await channel.send(commonMessageText + guildSummaryText + bottomMessageText)
                    
        self.__saveData()

    async def closeChampionship(self):
        if self.nextGrandPrix.round <= self.currGrandPrix.round:
            commonMessageText : str =   "🏆The championship is coming to a close! Well played everyone!👏\n\n"
            commonMessageText +=        "Here are the top 3 from our standings-"

            bottomMessageText : str =   "Thanks to all participants! See you next year!"

            for guild in self.__guildDict.values():
                if guild.autoUpdatesActive and self.__guildUpdateStatusDict[guild.guildID]:
                    guildSummaryText : str = guild.championshipSummary()
                    channel = self.get_channel(guild.updatesChannel)
                    if type(channel) == discord.TextChannel:
                        await channel.send(commonMessageText + guildSummaryText + bottomMessageText)

    async def sendNewSeasonUpdate(self):
        if self.nextGrandPrix.round == 1:
            commonMessageText : str =   "Hello everyone! Welcome to the " + str(self.nextGrandPrix.startTime.year) + " Points Championship!\n"
            commonMessageText +=        "**Note:** Latest predictions will be carried over from the previous year and new predictions can only be made during " +\
                        "the Grand Prix weekend. Once the race results are available, the points will be automatically be udpated accordingly.\n"
            commonMessageText +=        "If you wish to change this behavior, please ask the admins to modify it.\n"
            commonMessageText +=        "\n🔔See you next at the " + str(self.nextGrandPrix) + "(Round " +str(self.nextGrandPrix.round) + ") in " +\
                         self.nextGrandPrix.location + " on " + self.nextGrandPrix.raceDateTime_str() + "!"
            
            for guild in self.__guildDict.values():
                channel = self.get_channel(guild.updatesChannel)
                guild.autoUpdatesActive = True
                guild.adminOverrideFlag = OverrideState.NO_OVERRIDE
                guild.passivePredictionActive = True
                self.__guildUpdateStatusDict[guild.guildID] = True
                if type(channel) == discord.TextChannel:
                    await channel.send(commonMessageText)

        self.__saveData()


    async def on_ready(self):
        print("Whatever")

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return
        
        for command in USER_COMMANDS:
            if message.content.startswith(command):
                await self.__userCommandHandler(message)
                return
        
        for command in ADMIN_COMMANDS:
            if message.content.startswith(command):
                await self.__adminCommandHandler(message)
                return

        else:
            await self._easterEggs(message)

    async def on_guild_join(self, guild : discord.Guild):
        if guild.id not in self.__guildDict.keys():
            server : Server = Server(guild.name, guild.id)
            self.__guildDict[guild.id] = server
            self.__guildUpdateStatusDict[guild.id] = False
            self.__saveData()

    async def on_member_remove(self, member : discord.Member):
        if member.guild:
            self.__guildDict[member.guild.id].removeUser(name = member.name)

    async def on_guild_remove(self, guild : discord.Guild):
        if guild.id in self.__guildDict.keys():
            del self.__guildDict[guild.id]
            self.__saveData()



    


