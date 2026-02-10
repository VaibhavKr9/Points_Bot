import subprocess
import argparse
import threading
import os
import dotenv

def run_script(script_name):
    subprocess.run(["python", script_name])


def getArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--branch", default="main")
    parser.add_argument("-ng","--no-git", action='store_false', dest="git_run")
    parser.add_argument("-f","--files", nargs='+', default=["main.py"])
    return parser.parse_args()

if __name__ == "__main__":

    dotenvFile = dotenv.find_dotenv()
    dotenv.set_key(dotenvFile, "PROJ_HOME", str(os.path.dirname(os.path.abspath(__file__))))

    args : argparse.Namespace = getArgs()

    if(args.git_run == True):
        subprocess.run(["git","fetch"])
        subprocess.run(["git","checkout","-f","origin/" + args.branch])

    threadList : list[threading.Thread] = []
    for script in args.files:
        threadList.append(threading.Thread(target=run_script, args=(script,)))
    
    for thread in threadList:
        thread.start()
    
    for thread in threadList:
        thread.join()