# encoding:utf-8
from fxdayu_ex.module.empty import *
from fxdayu_ex.module.instance import Structure
from fxdayu_ex.utils.json_adapt import JSONAdaptor


class ReqOrder(Structure, JSONAdaptor):

    __slots__ = ("accountID", "code", "qty", "price", "time", "info", "orderType", "bsType")
    DIRECT = ("accountID", "code", "qty", "price", "time", "info")
    ENUMS = ("orderType", "bsType")


    def __init__(self,
                 accountID=EMPTY_STR,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 price=EMPTY_INT,
                 orderType=EMPTY,
                 bsType=EMPTY,
                 time=EMPTY,
                 info=EMPTY):
        self.accountID = accountID
        self.code = code
        self.qty = qty
        self.price = price
        self.orderType = orderType
        self.bsType = bsType
        self.time = time
        self.info = info


class QryOrder:

    def __init__(self, accountID=EMPTY_STR, orderID=EMPTY_STR):
        self.accountID = accountID
        self.orderID = orderID


class CancelOrder(Structure, JSONAdaptor):

    __slots__ = ("accountID", "orderID")
    DIRECT = __slots__

    def __init__(self, accountID=EMPTY_STR, orderID=EMPTY_STR):
        self.accountID = accountID
        self.orderID = orderID


class QryTrade:

    def __init__(self, accountID=EMPTY_STR, orderID=EMPTY_STR):
        self.accountID = accountID
        self.orderID = orderID


class QryCash:

    def __init__(self, accountID=EMPTY_STR):
        self.accountID = accountID


class QryPosition:

    def __init__(self, accountID=EMPTY_STR, code=EMPTY_STR):
        self.accountID = accountID
        self.code = code


class ReqSnapshot(Structure, JSONAdaptor):

    __slots__ = ("accountID",)
    DIRECT = __slots__

    def __init__(self, accountID=EMPTY_STR):
        self.accountID = accountID


CLASSES = dict(
    map(lambda cls: (cls.__name__, cls),
        [ReqOrder, CancelOrder, QryOrder, QryCash, QryPosition, QryTrade, ReqSnapshot])
)


__all__ = ["ReqOrder", "CancelOrder", "QryOrder", "QryCash", "QryPosition", "QryTrade", "ReqSnapshot", "CLASSES"]
