import fastf1
from datetime import datetime
from datetime import timedelta
import os
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

class FastF1Data:
    def __init__(self):
        fastf1.Cache.enable_cache(f"{os.getenv("CACHE_DIR")}", force_renew=True)
        self.__year = datetime.now().year
        self.__round = 1
        self.__seasonStatus = SeasonStatus.NOT_STARTED
        self.__roundStatus = RoundStatus.NOT_STARTED
        self.__isUpdated = False

    def __updateData(self):
        self.__year = datetime.now().year
        calendar = fastf1.get_event_schedule(self.__year)
        now = datetime.now()
        for index, event in calendar.iterrows():
            self.__round = event['RoundNumber']
            if now < event['Session5DateUtc'].to_pydatetime() + timedelta(hours=4):
                if self.__round == 1:
                    self.__seasonStatus = SeasonStatus.NOT_STARTED
                else:
                    self.__seasonStatus = SeasonStatus.ONGOING

                if now < event['Session1DateUtc'].to_pydatetime():
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
                grandPrixEvent = fastf1.get_event(self.__year, self.__round)
            except:
                self.__roundStatus = RoundStatus.NOT_STARTED
                self.__seasonStatus = SeasonStatus.ENDED
                return None
            grandPrix = GrandPrix()
            grandPrix.name = grandPrixEvent['EventName']
            grandPrix.location = grandPrixEvent['Location']
            grandPrix.round = grandPrixEvent['RoundNumber']
            grandPrix.startTime = grandPrixEvent['Session1DateUtc'].to_pydatetime()
            grandPrix.raceTime = grandPrixEvent['Session5DateUtc'].to_pydatetime()
            grandPrix.qualiTime = grandPrixEvent['Session4DateUtc'].to_pydatetime()

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
                raceSession = fastf1.get_session(self.__year, self.__round, 'R')
            except:
                return None, None
            raceSession.load()
            if raceSession.results.empty == False:
                qualiResults = []
                raceResults = []
                for index, row in raceSession.results.iterrows():
                    if row['Position'] in [1, 2, 3]:
                        raceResults.append(row['Abbreviation'])
                    if row['GridPosition'] in [1, 2, 3]:
                        qualiResults.append(row['Abbreviation'])

                '''raceResults = raceSession.results["Abbreviation"].tolist()
                qualiSession = fastf1.get_session(self.__year, self.__round, 'Q')
                qualiSession.load()
                qualiResults = qualiSession.results["Abbreviation"].tolist()'''

                self.__roundStatus = RoundStatus.ENDED
                return (qualiResults, raceResults)
            else:
                return None, None
            
        return None, None
            
    def getTotalRounds(self) -> int:
        if not self.__isUpdated:
            self.__updateData()
        calendar = fastf1.get_event_schedule(self.__year)
        return calendar.tail(1)['RoundNumber'].values[0]

if __name__ == "__main__":
    '''calendar = fastf1.get_event_schedule(2025)
    print(calendar[['RoundNumber', 'EventName', 'Location', 'Session5DateUtc']])
    racetime = calendar.get_event_by__round(3)['Session5DateUtc'].to_pydatetime()
    print(racetime)'''
    f1data = FastF1Data()
    #f1data._updateData()
    f1data._FastF1Data__year = 2025
    f1data._FastF1Data__round = 3
    f1data._FastF1Data__isUpdated = True
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