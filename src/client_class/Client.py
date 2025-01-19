import discord
import logging
from os import path
import pickle
from datetime import datetime
from server_class.Server import Server
from server_class.Server import OverrideState
from grand_prix_class.GrandPrix import GrandPrix
import errors_class.Errors as err

class DiscordClient(discord.Client):
    def __init__(self):
        self._logHandler : logging.Handler = logging.FileHandler(filename="client.log", encoding="utf-8")
        self.intents.messages = True
        self.intents.guilds = True
        self.intents.members = True
        self.intents.message_content = True
        self._guildDict : dict[int : Server] = {}
        self._isActive : bool = False
        self._adminOverrideActive : bool = False
        self.currGrandPrix : GrandPrix = GrandPrix()
        self.nextGrandPrix : GrandPrix = GrandPrix()

    async def start(self, authKey : str, pickleFilePath : str) -> None:
        try:
            self.run(token= authKey, reconnect= True, log_handler= self._logHandler)
            await self.wait_until_ready()

            if path.isfile(pickleFilePath):
                with open(pickleFilePath, "rb") as pickleFile:
                    clientInfo = pickle.load(pickleFile)
                    self._guildDict = dict.fromkeys(clientInfo["guildIDList"])
                    self.currGrandPrix = clientInfo["currGrandPrix"]
                    self.nextGrandPrix = clientInfo["nextGrandPrix"]
                    for guildID in self._guildDict.keys():
                        guild = Server()
                        guild.loadData(guildID)
                        self._guildDict[guildID] = guild
                    self._isActive = True
            else:
                with open(pickleFilePath, "wb+") as pickleFile:
                    clientInfo = {"guildIDList"  : self._guildDict.keys(),
                                  "currGrandPrix": self.currGrandPrix,
                                  "nextGrandPrix": self.nextGrandPrix}
                    pickle.dump(clientInfo, pickleFile, pickle.HIGHEST_PROTOCOL)
                self._isActive = True

        except Exception as exception:
            print("Error in starting the client: ", exception)

    def isPredictionUpdateAllowed(self, tag : str) -> bool:
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
            
    async def _easterEggs(self, message : discord.Message):
        pass

        #TODO: Easter eggs


    async def on_ready():
        print("Whatever")

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return
        
        if message.content.startswith("!predict"):
            predList : list[str] = []
            userFound : bool = False
            [com, tag, predList[0], predList[1], predList[2]] = message.content.lower().split(" ")
            if self._adminOverrideActive or self.isPredictionUpdateAllowed(tag):
                for guild in self._guildDict.values():
                    for user in guild.players:
                        if message.author.id == int(user):
                            userFound = True
                            if (((guild.adminOverrideFlag == OverrideState.NO_OVERRIDE) and (self.isPredictionUpdateAllowed(tag))) or\
                                (guild.adminOverrideFlag == OverrideState.OPENED_BY_ADMIN)):
                                await message.channel.send(guild.updatePredictions(tag, predList, userName = message.author.name))
                            else:
                                await message.channel.send(self.currGrandPrix.predictionClosedMsg(tag) + " for " + guild.name)
                            break
                if not userFound:
                    await message.channel.send("You don't seem to be registered on any server.")
            else:
                await message.channel.send(self.currGrandPrix.predictionClosedMsg(tag))

        elif message.content.lower() == "!add me":
            if message.guild:
                if self._guildDict[message.guild.id].newUser(message.author.name, message.author.mention):
                    await message.channel.send("👋Welcome to the championship "+ message.author.mention + "!")
                else:
                    await message.channel.send("You are already registered in this server")
            else:
                await message.channel.send("Send this message on a channel of the server you want to take part in the championship of")

        elif message.author.guild_permissions.administrator == True:
            if message.content.startswith("!change"):
                predList : list[str] = []
                userFound : bool = False
                [com, tag, mention, predList[0], predList[1], predList[2]] = message.content.lower().split(" ")
                await message.channel.send(self._guildDict[message.guild.id].updatePredictions(tag, predList, mention = mention))

            elif message.content.startswith("!add"):
                [com, mention] = message.content.split(" ")
                async for member in message.guild.fetch_members():
                    if member.mention == mention:
                        if self._guildDict[message.guild.id].newUser(member.name, member.mention):
                            await message.channel.send("👋Welcome to the championship "+ member.mention + "!")
                        else:
                            await message.channel.send(member.name + " is already registered on the server.")

            elif message.content.lower() == "!open":
                self._guildDict[message.guild.id].adminOverrideFlag = OverrideState.OPENED_BY_ADMIN
                self._adminOverrideActive = True
            
            elif message.content.lower() == "!close":
                self._guildDict[message.guild.id].adminOverrideFlag = OverrideState.CLOSED_BY_ADMIN
                self._adminOverrideActive = True

            elif message.content.lower() == "!auto":
                self._guildDict[message.guild.id].adminOverrideFlag = OverrideState.NO_OVERRIDE
                self._adminOverrideActive = False
                for guild in self._guildDict.values():
                    if guild.adminOverrideFlag != OverrideState.NO_OVERRIDE:
                        self._adminOverrideActive = True
                        break


        else:
            await self._easterEggs(message)





    


