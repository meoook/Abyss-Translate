from typing import Callable


class TextQuoteFinder:
    """ Simple class to find quotes in texts (minimum 2 values needed to work) """
    def __init__(self):
        # Max quote length
        self.__left: int = 4
        self.__right: int = 4
        # Quote values
        self.__l1: str = ''
        self.__l2: str = ''
        self.__l3: str = ''
        self.__l4: str = ''

        self.__r1: str = ''
        self.__r2: str = ''
        self.__r3: str = ''
        self.__r4: str = ''

        self.__values_count: int = 0  # Can check after 2

    @staticmethod
    def function_to_unquote_text(quotes: str) -> Callable[[str], str]:
        """ Function to get text without quotes. Quotes are 2 digits - quote length from left/right side of text """
        quotes_l = int(quotes[0])
        quotes_r = int(quotes[1])

        def fn(text: str) -> str:
            if text and len(text) >= quotes_l + quotes_r:
                return text[quotes_l:-quotes_r] if quotes_r > 0 else text[quotes_l:]
            return ''

        return fn

    @property
    def value(self) -> str:
        """ Return quotes lengths """
        if self.__values_count > 1:
            return f'{self.__left}{self.__right}'
        else:
            return '00'

    @value.setter
    def value(self, value: str):
        """ Set new value to check quotes """
        if isinstance(value, str) and len(value) > 3:
            self.__values_count += 1
            if not self.__l1:   # Set quotes on first round
                [self.__l1, self.__l2, self.__l3, self.__l4] = value[:4]
                [self.__r4, self.__r3, self.__r2, self.__r1] = value[-4::1]
            else:
                self.__quotes_check_left(value)
                self.__quotes_check_right(value)

    def __quotes_check_left(self, value: str) -> None:
        if self.__left == 4:
            if self.__l4 != value[3]:
                self.__left = 3
        if self.__left >= 3:
            if self.__l3 != value[2]:
                self.__left = 2
        if self.__left >= 2:
            if self.__l2 != value[1]:
                self.__left = 1
        if self.__left >= 1:
            if self.__l1 != value[0]:
                self.__left = 0

    def __quotes_check_right(self, value: str) -> None:
        if self.__right == 4:
            if self.__r4 != value[-4]:
                self.__right = 3
        if self.__right >= 3:
            if self.__r3 != value[-3]:
                self.__right = 2
        if self.__right >= 2:
            if self.__r2 != value[-2]:
                self.__right = 1
        if self.__right >= 1:
            if self.__r1 != value[-1]:
                self.__right = 0
