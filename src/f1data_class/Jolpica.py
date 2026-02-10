import requests
from datetime import datetime
from datetime import timedelta
import enum
from grand_prix_class.GrandPrix import GrandPrix



class SeasonStatus(enum.Enum):
    NOT_STARTED = 0
    ONGOING = 1
    ENDED = 2

class RoundStatus(enum.Enum):
    NOT_STARTED = 0
    ONGOING = 1
    ENDED = 2

class JolpicaData:
    def __init__(self):
        self.__year = datetime.now().year
        self.__round = 1
        self.__seasonStatus = SeasonStatus.NOT_STARTED
        self.__roundStatus = RoundStatus.NOT_STARTED
        self.__isUpdated = False

    def __apiStrToDateTime(self, dateStr: str, timeStr: str) -> datetime:
        return datetime.strptime(dateStr + " " + timeStr, "%Y-%m-%d %H:%M:%SZ")

    def __updateData(self):
        self.__year = datetime.now().year
        currentSeason = requests.get("https://api.jolpi.ca/ergast/f1/current.json").json()
        currentRaceList = currentSeason["MRData"]["RaceTable"]["Races"]
        now = datetime.now()
        for event in currentRaceList:
            self.__round = event["round"]
            raceTime = self.__apiStrToDateTime(event["date"], event["time"])
            FP1Time = self.__apiStrToDateTime(event["FirstPractice"]["date"], event["FirstPractice"]["time"])
            if now < raceTime + timedelta(hours=4):
                if self.__round == 1:
                    self.__seasonStatus = SeasonStatus.NOT_STARTED
                else:
                    self.__seasonStatus = SeasonStatus.ONGOING

                if now < FP1Time:
                    self.__roundStatus = RoundStatus.NOT_STARTED
                else:
                    self.__roundStatus = RoundStatus.ONGOING
                self.__isUpdated = True
                return
        self.__seasonStatus = SeasonStatus.ENDED
        self.__roundStatus = RoundStatus.NOT_STARTED
        self.__round += 1
        self.__isUpdated = True

    def getNextGrandPrix(self) -> GrandPrix | None:
        if not self.__isUpdated:
            self.__updateData()
        if self.__seasonStatus != SeasonStatus.ENDED and self.__roundStatus != RoundStatus.ENDED:
            try:
                grandPrixEvent = requests.get(f"https://api.jolpi.ca/ergast/f1/{self.__year}/{self.__round}.json").json()["MRData"]["RaceTable"][0]
            except:
                self.__roundStatus = RoundStatus.NOT_STARTED
                self.__seasonStatus = SeasonStatus.ENDED
                return None
            grandPrix = GrandPrix()
            grandPrix.name = grandPrixEvent["raceName"]
            grandPrix.location = grandPrixEvent["Circuit"]["Location"]["locality"]
            grandPrix.round = int(grandPrixEvent["round"])
            grandPrix.startTime = self.__apiStrToDateTime(grandPrixEvent["FirstPractice"]["date"], grandPrixEvent["FirstPractice"]["time"])
            grandPrix.raceTime = self.__apiStrToDateTime(grandPrixEvent["date"], grandPrixEvent["time"])
            grandPrix.qualiTime = self.__apiStrToDateTime(grandPrixEvent["Qualifying"]["date"], grandPrixEvent["Qualifying"]["time"])

            now = datetime.now()
            if self.__round == 1 and now < grandPrix.startTime:
                self.__seasonStatus = SeasonStatus.NOT_STARTED
            else:
                self.__seasonStatus = SeasonStatus.ONGOING

            if now < grandPrix.startTime:
                self.__roundStatus = RoundStatus.NOT_STARTED
            elif now < grandPrix.raceTime + timedelta(hours=4):
                self.__roundStatus = RoundStatus.ONGOING
            else:
                self.__roundStatus = RoundStatus.ENDED
                return self.getNextGrandPrix()
                
            return grandPrix
        elif self.__roundStatus == RoundStatus.ENDED:
            self.__roundStatus = RoundStatus.NOT_STARTED
            self.__round += 1
            return self.getNextGrandPrix()
        else:
            return None
        
    def getNewSeasonGrandPrix(self) -> GrandPrix | None:
        if not self.__isUpdated:
            self.__updateData()
        self.__roundStatus = RoundStatus.NOT_STARTED
        self.__seasonStatus = SeasonStatus.NOT_STARTED
        if self.__year < datetime.now().year:
            self.__year = datetime.now().year
            self.__round = 1
            return self.getNextGrandPrix()
        return None
            
    def getCurrentGrandPrixResults(self) -> tuple[list[str] | None, list[str] | None]:
        if not self.__isUpdated:
            self.__updateData()
        if self.__seasonStatus != SeasonStatus.ENDED and self.__roundStatus != RoundStatus.ENDED:
            try:
                print("Fetching results for Year", self.__year, " Round ", self.__round)
                raceDriversList = requests.get(f"https://api.jolpi.ca/ergast/f1/{self.__year}/{self.__round}/results.json").json()["MRData"]["RaceTable"]["Races"][0]["Results"]
            except Exception as e:
                print(e)
                return None, None

            if raceDriversList != None:
                gridResults = ["000", "000", "000"]
                raceResults = ["000", "000", "000"]
                for driver in raceDriversList:
                    if int(driver["position"]) < 4:
                        raceResults[int(driver["position"]) - 1] = driver["Driver"]["code"]
                    if int(driver["grid"]) < 4:
                        gridResults[int(driver["grid"]) - 1] = driver["Driver"]["code"]

                self.__roundStatus = RoundStatus.ENDED
                return (gridResults, raceResults)
            else:
                return None, None
            
        return None, None
            
    def getTotalRounds(self) -> int:
        if not self.__isUpdated:
            self.__updateData()
        currentSeason = requests.get("https://api.jolpi.ca/ergast/f1/current.json").json()
        return int(currentSeason["MRData"]["total"])

if __name__ == "__main__":
    '''calendar = fastf1.get_event_schedule(2025)
    print(calendar[['RoundNumber', 'EventName', 'Location', 'Session5DateUtc']])
    racetime = calendar.get_event_by__round(3)['Session5DateUtc'].to_pydatetime()
    print(racetime)'''
    f1data = JolpicaData()
    #f1data._updateData()
    f1data._JolpicaData__year = 2025
    f1data._JolpicaData__round = 3
    f1data._JolpicaData__isUpdated = True
    currentGPResults = f1data.getCurrentGrandPrixResults()
    print(currentGPResults)
    '''nextGP = f1data.getNextGrandPrix()
    print(nextGP)
    print(nextGP.raceTime)
    nextGP = f1data.getNextGrandPrix()
    print(nextGP)
    print(nextGP.raceTime)
    currentGPResults = f1data.getCurrentGrandPrixResults()
    print(currentGPResults)'''