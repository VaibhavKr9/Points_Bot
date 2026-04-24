from dotenv import load_dotenv
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio
import logging

from src.grand_prix_class.GrandPrix import GrandPrix
from src.client_class.Client import DiscordClient
from src.f1data_class.FastF1 import FastF1Data

load_dotenv()

dataAPI = FastF1Data()
pointsBotClient = DiscordClient()

logger = logging.getLogger("scheduler")
logger.setLevel(logging.DEBUG)
scheduler = AsyncIOScheduler()

async def scheduleBroadcastTask():
    global pointsBotClient
    pointsBotClient.moveToNextGrandPrix()
    await pointsBotClient.sendSchedule()
    scheduler.add_job(closeQualiPredictionsBroadcastTask, 'date', run_date=pointsBotClient.currGrandPrix.qualiTime)
    logger.info(str(pointsBotClient.currGrandPrix) + " started. Schedule sent and close quali predictions task scheduled for " +\
                pointsBotClient.currGrandPrix.qualiTime.strftime("%Y-%m-%d %H:%M:%S"))

async def closeQualiPredictionsBroadcastTask():
    await pointsBotClient.closePredictions('grid')
    scheduler.add_job(closeRacePredictionsBroadcastTask, 'date', run_date=pointsBotClient.currGrandPrix.raceTime)
    logger.info(str(pointsBotClient.currGrandPrix) + " Quali predictions closed. Close race predictions task scheduled for " +\
                pointsBotClient.currGrandPrix.raceTime.strftime("%Y-%m-%d %H:%M:%S"))

async def closeRacePredictionsBroadcastTask():
    await pointsBotClient.closePredictions('race')
    scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=pointsBotClient.currGrandPrix.raceTime + timedelta(hours=3))
    logger.info(str(pointsBotClient.currGrandPrix) + " Race predictions closed. Results check task scheduled for " +\
                (pointsBotClient.currGrandPrix.raceTime + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"))

async def checkGrandPrixResultsTask():
    now = datetime.now()
    gridResults, raceResults = dataAPI.getCurrentGrandPrixResults()

    if gridResults is not None and raceResults is not None:
        logger.info("Latest Grand Prix results received.")
        nextGP = dataAPI.getNextGrandPrix()
        if nextGP is not None:
            pointsBotClient.updateNextGrandPrix(nextGP, dataAPI.getTotalRounds())
            logger.info("Next Grand Prix updated to " + str(nextGP))
        result = await pointsBotClient.updateResults(gridResults, raceResults)

        if result and nextGP is None:
            result = await pointsBotClient.closeChampionship()
            logger.info("Next Grand Prix not found, closing championship.")

        if result and nextGP is not None:
            if not pointsBotClient.areAllServersUpdated() and now < pointsBotClient.nextGrandPrix.startTime - timedelta(hours=4):
                scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=now + timedelta(hours=2))
                logger.info("All servers not updated, rescheduling results check task for " + (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"))
            else:
                scheduler.add_job(scheduleBroadcastTask, 'date', run_date=pointsBotClient.nextGrandPrix.startTime)
                logger.info("All servers updated or next Grand Prix starting soon, scheduling schedule broadcast task for " +\
                            pointsBotClient.nextGrandPrix.startTime.strftime("%Y-%m-%d %H:%M:%S"))
        elif result and nextGP is None:
            if not pointsBotClient.areAllServersUpdated() and now < pointsBotClient.currGrandPrix.raceTime + timedelta(weeks=2):
                scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=now + timedelta(hours=2))
                logger.info("All servers not updated, rescheduling results check task for " + (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"))
            else:
                scheduler.add_job(newSeasonTask, 'date', run_date=datetime(year=now.year + 1, month=2, day=15))
                logger.info("All server championships closed or 2 weeks passed since season ended, scheduling new season task for " +\
                            datetime(year=now.year + 1, month=2, day=15).strftime("%Y-%m-%d %H:%M:%S"))
        
    else:
        scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=now + timedelta(hours=1))
        logger.info("Latest Grand Prix results not yet updated, rescheduling results check task for " +\
                    (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))

async def newSeasonTask():
    nextGP = dataAPI.getNewSeasonGrandPrix()
    
    if nextGP is not None:
        pointsBotClient.updateNextGrandPrix(nextGP, dataAPI.getTotalRounds())
        await pointsBotClient.sendNewSeasonUpdate()
        scheduler.add_job(scheduleBroadcastTask, 'date', run_date=pointsBotClient.nextGrandPrix.startTime)
        logger.info("New season schedule available, scheduling schedule broadcast task for " +\
                            pointsBotClient.nextGrandPrix.startTime.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        scheduler.add_job(newSeasonTask, 'date', run_date=datetime.now() + timedelta(weeks=1))
        logger.info("New season schedule not found, next check scheduled for " +\
                            (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M:%S"))

async def pingUser():
    userID = int(os.getenv("USER_ID"))
    if pointsBotClient.is_ready() and userID is not None:
    	await pointsBotClient.pingUser(userID)
    else:
        await asyncio.sleep(5)
        await pingUser()
        
def enterSchedulingCycle():
    global scheduler
    now = datetime.now()
    logger.info("Starting scheduling cycle...")
    
    scheduler.add_job(pingUser, 'date', run_date=now + timedelta(seconds=20))

    if now < datetime(year=now.year, month=2, day=15):
        scheduler.add_job(newSeasonTask, 'date', run_date=datetime(year=now.year, month=2, day=15))
        logger.info("New season task scheduled for " + datetime(year=now.year, month=2, day=15).strftime("%Y-%m-%d %H:%M:%S"))
    else:
        nextGP = dataAPI.getNextGrandPrix()
        if nextGP is None and now > datetime(year=now.year, month=10, day=1):
            scheduler.add_job(newSeasonTask, 'date', run_date=datetime(year=now.year + 1, month=2, day=15))
            logger.info("New season task scheduled for " + datetime(year=now.year + 1, month=2, day=15).strftime("%Y-%m-%d %H:%M:%S"))
        elif nextGP is None:
            scheduler.add_job(newSeasonTask, 'date', run_date=now + timedelta(hours=48))
            logger.info("New season task scheduled for " + (now + timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S"))
        else:
            if now < nextGP.startTime:
                if pointsBotClient.nextGrandPrix.startTime < now:
                    pointsBotClient.updateNextGrandPrix(nextGP, dataAPI.getTotalRounds())
                    logger.info("Next Grand Prix updated to " + str(nextGP))
                scheduler.add_job(scheduleBroadcastTask, 'date', run_date=nextGP.startTime)
                logger.info("Schedule broadcast task scheduled for " + nextGP.startTime.strftime("%Y-%m-%d %H:%M:%S"))
            elif now < nextGP.qualiTime:
                scheduler.add_job(closeQualiPredictionsBroadcastTask, 'date', run_date=nextGP.qualiTime)
                logger.info("Close quali predictions broadcast task scheduled for " + nextGP.qualiTime.strftime("%Y-%m-%d %H:%M:%S"))
            elif now < nextGP.raceTime:
                scheduler.add_job(closeRacePredictionsBroadcastTask, 'date', run_date=nextGP.raceTime)
                logger.info("Close race predictions broadcast task scheduled for " + nextGP.raceTime.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                scheduler.add_job(checkGrandPrixResultsTask, 'date', run_date=now + timedelta(seconds=20))
                logger.info(str(pointsBotClient.currGrandPrix) + " Race started. Results check task scheduled for " +\
                (now + timedelta(seconds=20)).strftime("%Y-%m-%d %H:%M:%S"))

async def enterAsyncLoop():
    global scheduler, pointsBotClient
    botAuthKey = os.getenv("DISCORD_BOT_TOKEN")
    print("Logging into client...")
    await pointsBotClient.startClient(botAuthKey, f"{os.getenv("PICKLE_DIR")}/client.pickle", f"{os.getenv("LOG_DIR")}/client.log")
    print("Starting scheduler...")
    scheduler.start()
    while not scheduler.running:
        pass
    print("Connecting to socket...")
    await pointsBotClient.connectClient()

def startBot():
    global dataAPI, pointsBotClient, scheduler, logger

    logHandler = logging.FileHandler(f"{os.getenv("LOG_DIR")}/scheduler.log")
    logHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(logHandler)

    dataAPI = FastF1Data(True)
    enterSchedulingCycle()
    asyncio.run(enterAsyncLoop())
    



