from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import asyncio

from grand_prix_class.GrandPrix import GrandPrix
from client_class.Client import DiscordClient
from src.f1data_class.FastF1 import FastF1Data

load_dotenv()

dataAPI = FastF1Data()
pointsBotClient = DiscordClient()

scheduler = BackgroundScheduler()

def scheduleBroadcastTask():
    global pointsBotClient
    pointsBotClient.moveToNextGrandPrix()
    asyncio.run(pointsBotClient.sendSchedule())
    scheduler.add_job(closeQualiPredictionsBroadcastTask, 'date', run_date=pointsBotClient.currGrandPrix.qualiTime)

def closeQualiPredictionsBroadcastTask():
    asyncio.run(pointsBotClient.closePredictions('grid'))
    scheduler.add_job(closeRacePredictionsBroadcastTask, 'date', run_date=pointsBotClient.currGrandPrix.raceTime)

def closeRacePredictionsBroadcastTask():
    asyncio.run(pointsBotClient.closePredictions('race'))
    scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=pointsBotClient.currGrandPrix.raceTime + timedelta(hours=3))

def checkGrandPrixResultsTask():
    gridResults, raceResults = dataAPI.getCurrentGrandPrixResults()

    if gridResults is not None and raceResults is not None:
        nextGP = dataAPI.getNextGrandPrix()
        if nextGP is not None:
            pointsBotClient.updateNextGrandPrix(nextGP, dataAPI.getTotalRounds())
        result = asyncio.run(pointsBotClient.updateResults(gridResults, raceResults))

        if result and nextGP is None:
            result = asyncio.run(pointsBotClient.closeChampionship())

        if result and nextGP is not None:
            if not pointsBotClient.areAllServersUpdated() and datetime.now() < pointsBotClient.nextGrandPrix.startTime - timedelta(hours=4):
                scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=datetime.now() + timedelta(hours=2))
            else:
                scheduler.add_job(scheduleBroadcastTask, 'date', run_date=pointsBotClient.nextGrandPrix.startTime)
        elif result and nextGP is None:
            if not pointsBotClient.areAllServersUpdated() and datetime.now() < pointsBotClient.currGrandPrix.raceTime + timedelta(weeks=2):
                scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=datetime.now() + timedelta(hours=2))
            else:
                scheduler.add_job(newSeasonTask, 'date', run_date=datetime(year=datetime.now().year + 1, month=2, day=15))
        
    else:
        scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=datetime.now() + timedelta(hours=1))

def newSeasonTask():
    nextGP = dataAPI.getNewSeasonGrandPrix()
    
    if nextGP is not None:
        pointsBotClient.updateNextGrandPrix(nextGP, dataAPI.getTotalRounds())
        asyncio.run(pointsBotClient.sendNewSeasonUpdate())
        scheduler.add_job(scheduleBroadcastTask, 'date', run_date=pointsBotClient.nextGrandPrix.startTime)
    else:
        scheduler.add_job(newSeasonTask, 'date', run_date=datetime.now() + timedelta(weeks=1))

def enterSchedulingCycle():
    now = datetime.now()
    if now < datetime(year=now.year, month=2, day=15):
        scheduler.add_job(newSeasonTask, 'date', run_date=datetime(year=now.year, month=2, day=15))
    else:
        nextGP = dataAPI.getNextGrandPrix()
        if nextGP is None and now > datetime(year=now.year, month=10, day=1):
            scheduler.add_job(newSeasonTask, 'date', run_date=datetime(year=datetime.now().year + 1, month=2, day=15))
        elif nextGP is None:
            scheduler.add_job(newSeasonTask, 'date', run_date=datetime.now() + timedelta(hours=48))
        else:
            if now < nextGP.startTime:
                if pointsBotClient.nextGrandPrix.startTime < now:
                    pointsBotClient.updateNextGrandPrix(nextGP, dataAPI.getTotalRounds())
                scheduler.add_job(scheduleBroadcastTask, 'date', run_date=nextGP.startTime)
            elif now < nextGP.raceTime:
                scheduler.add_job(closeRacePredictionsBroadcastTask, 'date', run_date=nextGP.raceTime)
            else:
                checkGrandPrixResultsTask()

if __name__ == "__main__":
    if os.getenv("DISCORD_BOT_TOKEN") is None:
        print("ERROR: DISCORD_BOT_TOKEN not found in environment variables.")
        exit(1)
    else:
        botAuthKey = os.getenv("DISCORD_BOT_TOKEN")
        pointsBotClient.startClient(botAuthKey, "data/pickles/client.pickle")
        enterSchedulingCycle()



