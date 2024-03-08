from datetime import datetime

from Order import Order


class GrandPrix:
    def __init__(self):
        self.name = ""
        self.location = ""
        self.round = 0
        self.qualiTime = datetime.now()
        self.raceTime = datetime.now()
        self.qualiResult = Order()
        self.raceResult = Order()

    def __str__(self):
        return self.name

    def qualiTime_str(self):
        return self.qualiTime.strftime("%a, %H:%M")

    def raceTime_str(self):
        return self.raceTime.strftime("%a, %H:%M")

    def raceDateTime_str(self):
        return self.raceTime.strftime("%d %B, %H:%M")

    def incrementRound(self):
        self.round = self.round + 1
