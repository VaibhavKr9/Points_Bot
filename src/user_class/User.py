from copy import deepcopy
from math import log10

from order_class.Order import Order
from countback_class.Countback import Countback
from errors_class.Errors import InvalidLengthException
from errors_class.Errors import InvalidPositionException


class User:
    """
    Description
    ------------
    Main class to save all user related data.

    Can be compared to other objects of the same class. The greater object
    is the one with the greater number of points and if the name of points is
    same, the countbacks are compared.

    Attributes
    ----------
    name: str
        User name (primary key)

    mention: str
        Numerical value to mention a user in a server

    gridPrediction: Order
        Latest prediction for grid finish

    racePrediction: Order
        Latest prediction for race finish


    Methods
    ---------
    updateGridPred(gridPred: Order) -> str
        Updates grid predictions of the user and return the confirmation
        message

    updateRacePred(racePred: Order) -> str
        Updates race predictions of the user and return the confirmation
        message

    updatePoints(gridResult: Order, raceResult: Order) -> None
        Updates the points and countback for the user as per results

    updatePosition(newPos: int) -> None
        Updates the position of the user in the server
    """

    def __init__(self):
        self.id: int = 0
        self.name: str = ""
        self.mention: str = ""
        self.__points: int = 0
        self.__weekPoints: int = 0
        self.__weekWins: int = 0
        self.__countback: Countback = Countback()
        self.__weekCountback: Countback = Countback()
        self.gridPrediction: Order = Order()
        self.racePrediction: Order = Order()
        self.currPosition: int = 0
        self.prevPosition: int = 0
        self.weekPosition: int = 0

    def __str__(self) -> str:
        return self.name
    
    def __int__(self) -> int:
        return self.id

    def incrementWins(self) -> None:
        """
        Increments the weekend wins for the user
        """

        self.__weekWins = self.__weekWins + 1

    def updateGridPred(self, QualiPred: Order) -> str:
        """
        Updates the grid prediction made by the user

        Arguments
        ---------
        gridPred: Order
            The new prediction as an Order
        
        Returns
        ----------
        A message which confirms that the change has been registered.
        """

        self.gridPrediction.updateFromOrder(QualiPred)
        msg = "✅ Grid prediction by" + self.name + \
            ": " + str(self.gridPrediction)
        return msg

    def updateRacePred(self, RacePred: Order) -> str:
        """
        Updates the race prediction made by the user

        Arguments
        ---------
        gridPred: Order
            The new prediction as an Order
        
        Returns
        ----------
        A message which confirms that the change has been registered.
        """

        self.racePrediction.updateFromOrder(RacePred)
        msg = "✅ Race prediction by" + self.name + \
            ": " + str(self.racePrediction)
        return msg

    def updatePoints(self, gridResult: Order, raceResult: Order) -> None:
        """
        Updates the weekend points and countback as well as overall points
        and countback. 
        The pointing scheme is-

            1. 1 point if the driver is in the result and also the prediction.
            2. 1 point if the driver is in the same position in the result and the prediction

        The countback scheme is-
            For every driver's position correctly predicted in the race result,
            1 countback point is given for that position.

        Arguments
        ----------
        gridResult: Order
            An order of the grid result

        raceResult: Order
            An order of the race result

        """
        self.__weekPoints = 0
        self.weekPosition = 0
        self.__weekCountback.clear()
        for pos in range(start=1, stop=4):
            if gridResult.driver(pos) == self.gridPrediction.driver(pos):
                self.__weekPoints = self.__weekPoints + 1
            if gridResult.driver(pos) in self.gridPrediction.orderList():
                self.__weekPoints = self.__weekPoints + 1
            if raceResult.driver(pos) == self.racePrediction.driver(pos):
                self.__weekPoints = self.__weekPoints + 1
                self.__weekCountback.increment(pos)
                self.__countback.increment(pos)
            if raceResult.driver(pos) in self.racePrediction.orderList():
                self.__weekPoints = self.__weekPoints + 1
        self.__points = self.__points + self.__weekPoints

    def __gt__(self, other) -> bool:
        if self.__points != other.__points:
            return self.__points > other.__points
        else:
            return self.__countback > other.__countback

    def __lt__(self, other) -> bool:
        if self.__points != other.__points:
            return self.__points < other.__points
        else:
            return self.__countback < other.__countback

    def __eq__(self, other) -> bool:
        return False
    
    def greaterWeekendThan(self, other) -> bool:
        if self.__weekPoints != other.__weekPoints:
            return self.__weekPoints > other.__weekPoints
        else:
            return self.__weekCountback > other.__weekCountback
        
    def equalWeekendTo(self, other) -> bool:
        if self.__weekPoints != other.__weekPoints:
            return False
        else:
            return self.__weekCountback == other.__weekCountback

    def updatePosition(self, newPos: int) -> None:
        """
        Updates the position of the user in the standings in currPosition 
        and saves the previous position in prevPosition.
        """

        if newPos < 1:
            raise InvalidPositionException
        else:
            self.prevPosition = self.currPosition
            self.currPosition = newPos

    def updateWeekPosition(self, weekPos:int) -> None:
        """
        Updates the position of the use in the weekend standings.
        """
        if weekPos < 1:
            raise InvalidPositionException
        else:
            self.weekPosition = weekPos

    def manualUpdatePoints(self, newPoints : int) -> str:
        if newPoints >= 0:
            self.__points = newPoints
            return "Points updated for " + self.name + " to " + str(self.__points) + "."
        return "Enter valid points input."

    def resetPredictions(self) -> None:
        """
        Resets the predictions of the user for a new Grand Prix weekend.
        """

        self.gridPrediction = Order()
        self.racePrediction = Order()

    def weekSummary(self) -> str:
        sum: str = ""
        sum += ": >".format(str(self.weekPosition)) + " | "
        sum += ": <30".format(self.name) + " | "
        sum += ": >3".format(str(self.__weekPoints)) + " | "
        sum += str(self.__weekCountback)

        return sum

    def summary(self) -> str:
        sum: str = ""
        if(self.prevPosition > self.currPosition): sum = "🔼 "
        elif(self.prevPosition < self.currPosition): sum = "🔽 "
        else: sum = "⏹ "

        sum += ": >3".format(str(self.currPosition)) + " | "
        sum += ": <30".format(self.name) + " | "
        sum += ": >6".format(str(self.__points)) + " | "
        sum += str(self.__countback)

        return sum
    
    def getWeekendPoints(self) -> int:
        return self.__weekPoints
    
    def getTotalPoints(self) -> int:
        return self.__points

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result