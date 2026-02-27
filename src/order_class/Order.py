from datetime import datetime
from datetime import timedelta
from copy import deepcopy

from src.errors_class.Errors import InvalidPositionException
from src.errors_class.Errors import InvalidLengthException


class Order:
    """
    Class to store an order of three-letter abbr. of drivers.

    The order is stored in a private member for abstraction and protection.

    Attributes
    ----------
    lastModified: datetime
        Stores the time this order was last modified

    Methods
    ----------
    update(pos: int, driver: str) -> None
        Updates the value at position pos with driver

    updateFromOrder(order: Order) -> None
        Updates all values from another Order object

    updateFromList(orderList: list[str]) -> None
        Updates all values from a list of drivers

    driver(pos: int) -> str
        Returns the value at position pos

    orderList(None) -> list[str]
        Returns an ordered list of all values

    modifiedTime_str(None) -> str
        Returns the last modified time as a string in IST off-shift.
    """

    def __init__(self):
        """
        Initializes the order with 000, 000, 000
        """

        self.__orderDict: dict[int, str] = {
            1: "000",
            2: "000",
            3: "000"
        }
        self.lastModified: datetime = datetime.now()

    def update(self, pos: int, driver: str) -> None:
        """
        Updates the value at position pos with driver. N0T recommended to be used.

        Method to update values, largely to be used by other methods
        of the same class.

        Arguments
        ---------
        pos: int
            Position of the value to be changed

        driver: str
            New value
        
        Returns
        ---------
        None

        Raises
        ---------
        InvalidPositionException
            To protect from KeyError

        InvalidLengthException
            To make sure the value is a three-letter abbr.
        """

        if (pos > 0) and (pos < 4):
            if len(driver) == 3:
                self.__orderDict[pos] = driver.upper()
                self.lastModified = datetime.now()
            else:
                raise InvalidLengthException
        else:
            raise InvalidPositionException

    def updateFromOrder(self, order: 'Order') -> None:
        """
        Updates all values from another Order object
        """

        self.__orderDict = deepcopy(order.__orderDict)
        self.lastModified = datetime.now()

    def updateFromList(self, orderList: list[str]):
        """
        Updates all values from a list of values
        
        Raises
        -------
        InvalidLengthException
            To make sure the value is a three-letter abbr.
        """

        #TODO: Check for the length of the list
        for pos, driver in enumerate(orderList, start=1):
            try:
                self.update(pos, driver)
            except InvalidLengthException:
                raise InvalidLengthException

    def __str__(self) -> str:
        return str(" ".join(driver for driver in self.__orderDict.values()))

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
    
    def driver(self, pos: int) -> str:
        """
        Returns the value at position pos
        """

        return self.__orderDict[pos]

    def orderList(self) -> list[str]:
        """
        Returns the order as a list of values
        """

        return self.__orderDict.values()

    #TODO: Redundant method
    def modifiedTime(self) -> datetime:
        return self.lastModified

    def modifiedTime_str(self) -> str:
        """
        Returns the last modfied time as a string with IST offset
        """
        
        return (self.lastModified + timedelta(hours=5.5)).strftime("%d-%b-%y, %a, %H:%M")
