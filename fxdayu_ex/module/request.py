# encoding:utf-8
from fxdayu_ex.module.empty import *
from fxdayu_ex.module.enums import *
from fxdayu_ex.module.instance import Structure
from fxdayu_ex.utils.json_adapt import JSONAdaptor
from datetime import datetime


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ReqOrder(Structure, JSONAdaptor):

    __slots__ = ("accountID", "code", "qty", "price", "time", "info", "orderType", "bsType")
    DIRECT = ("accountID", "code", "qty", "price", "time", "info")
    ENUMS = (("orderType", OrderType), ("bsType", BSType))


    def __init__(self,
                 accountID=EMPTY_INT,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 price=EMPTY_INT,
                 orderType=OrderType.LIMIT,
                 bsType=BSType.BUY,
                 time=EMPTY,
                 info=EMPTY_STR):
        self.accountID = accountID
        self.code = code
        self.qty = qty
        self.price = price
        self.orderType = orderType
        self.bsType = bsType
        self.time = time if time is not None else now()
        self.info = info


class QryOrder:

    def __init__(self, accountID=EMPTY_INT, orderID=EMPTY_INT):
        self.accountID = accountID
        self.orderID = orderID


class CancelOrder(Structure, JSONAdaptor):

    __slots__ = ("accountID", "orderID")
    DIRECT = __slots__

    def __init__(self, accountID=EMPTY_INT, orderID=EMPTY_INT):
        self.accountID = accountID
        self.orderID = orderID


class QryTrade:

    def __init__(self, accountID=EMPTY_INT, orderID=EMPTY_INT):
        self.accountID = accountID
        self.orderID = orderID


class QryCash:

    def __init__(self, accountID=EMPTY_INT):
        self.accountID = accountID


class QryPosition:

    def __init__(self, accountID=EMPTY_INT, code=EMPTY_INT):
        self.accountID = accountID
        self.code = code


class ReqSnapshot(Structure, JSONAdaptor):

    __slots__ = ("accountID",)
    DIRECT = __slots__

    def __init__(self, accountID=EMPTY_INT):
        self.accountID = accountID


CLASSES = dict(
    map(lambda cls: (cls.__name__, cls),
        [ReqOrder, CancelOrder, QryOrder, QryCash, QryPosition, QryTrade, ReqSnapshot])
)


__all__ = ["ReqOrder", "CancelOrder", "QryOrder", "QryCash", "QryPosition", "QryTrade", "ReqSnapshot", "CLASSES"]
