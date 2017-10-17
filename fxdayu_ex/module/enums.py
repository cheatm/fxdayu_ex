# encoding:utf-8
from enum import Enum


class BSType(Enum):

    SELL = 0
    BUY = 1


class OrderType(Enum):

    LIMIT = 0
    MARKET = 1


class OrderStatus(Enum):

    UNFILLED = 0
    PFILLED = 1
    FILLED = 2
    CANCELED = 3
