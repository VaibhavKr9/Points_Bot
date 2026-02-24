import os
import dotenv
from src import run

if __name__ == "__main__":
    HOME_DIR = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isdir(f"{HOME_DIR}/src"):
        print("ERROR: No src directory found. Exiting program.")
        exit(1)
    
    if not os.path.isfile(f"{HOME_DIR}/.env"):
        print("ERROR: No .env file found. Exiting program.")
        exit(1)
    else:
        dotenv.load_dotenv(f"{HOME_DIR}/.env")
        if os.getenv("DISCORD_BOT_TOKEN") is None:
            print("ERROR: DISCORD_BOT_TOKEN not found in environment variables. Exiting program.")
            exit(1)

    if not os.path.isdir(f"{HOME_DIR}/pickles"):
        os.makedirs(f"{HOME_DIR}/pickles")
    os.putenv("PICKLE_DIR", f"{HOME_DIR}/pickles")

    if not os.path.isdir(f"{HOME_DIR}/logs"):
        os.makedirs(f"{HOME_DIR}/logs")
    os.putenv("LOG_DIR", f"{HOME_DIR}/logs")

    if not os.path.isdir(f"{HOME_DIR}/cache"):
        os.makedirs(f"{HOME_DIR}/cache")
    os.putenv("CACHE_DIR", f"{HOME_DIR}/cache")

    os.putenv("HOME_DIR", HOME_DIR)

    run.startBot()

    