from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]

    @classmethod
    def values(cls):
        return list(i.value for i in cls)

    @classmethod
    def mapping(cls):
        return dict((i.name, i.value) for i in cls)

class TipsEnum(BaseEnum):
    BTS = "BTS"
    NBTS = "NBTS"
    U2 = "-2.5"
    O2 = "+2.5"
    ONE = "1"
    X = "x"
    TWO = "2"

class CurrencyEnum(BaseEnum):
    NGN = "NGN"
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"