import random

from errors_class.Errors import InvalidPositionException


class Countback:
    """
    Manages the countback values associated with a user.

    The values are stored in a private member for asbraction and protection.
    Countbacks can be directly compared, useful in determining the standings
    of the users. They can never be equal since in the case of having the same
    values, a random value will be returned.

    Attributes
    ----------
    No public attributes

    Methods
    ----------
    increment(pos: int) -> None
        increments the countback value for position pos

    getCount(pos: int) -> int
        returns the countback value for the position pos

    clear(None) -> None
        resets all the values of the countback to 0
    
    """

    def __init__(self):
        """
        Intializes the countback object with all values as 0
        """

        self.__countback_dict: dict[int, int] = {
            1: 0,
            2: 0,
            3: 0
        }

    def increment(self, pos: int) -> None:
        """
        Increments the countback value of the position by 1.

        Arugments
        ---------
        pos: int
            position to be incremented

        Raises
        -------
        InvalidPositionException
            To protect from keyError
        """

        if (pos > 0) and (pos < 4):
            self.__countback_dict[pos] = self.__countback_dict[pos] + 1
        else:
            raise InvalidPositionException

    def clear(self) -> None:
        """
        Resets all values of the countback to 0
        """

        for pos in [1, 2, 3]:
            self.__countback_dict[pos] = 0 

    def getCount(self, pos: int) -> int:
        """
        Returns countback value for the position pos
        """

        return self.__countback_dict[pos]

    def __gt__(self, other) -> bool:
        for pos in [1, 2, 3]:
            if self.__countback_dict[pos] != other.__countback_dict[pos]:
                return self.__countback_dict[pos] > other.__countback_dict[pos]
        return random.choice([True, False])

    def __lt__(self, other) -> bool:
        for pos in [1, 2, 3]:
            if self.__countback_dict[pos] != other.__countback_dict[pos]:
                return self.__countback_dict[pos] < other.__countback_dict[pos]
        return random.choice([True, False])
    
    def __eq__(self, other) -> bool:
        for pos in [1, 2, 3]:
            if self.__countback_dict[pos] != other.__countback_dict[pos]:
                return False
        return True

    def __str__(self) -> str:
        """
        Returns the countback values in order of positions seperated by commas
        """

        return str(", ".join(str(count) for count in self.__countback_dict.values()))
