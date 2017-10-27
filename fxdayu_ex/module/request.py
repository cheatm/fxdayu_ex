# encoding:utf-8
from fxdayu_ex.module.empty import *
from fxdayu_ex.module.storage import Structure
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


class Snapshot(Structure, JSONAdaptor):

    __slots__ = ("accountID",)
    DIRECT = __slots__

    def __init__(self, accountID=EMPTY_STR):
        self.accountID = accountID


__all__ = ["ReqOrder", "CancelOrder", "QryOrder", "QryCash", "QryPosition", "QryTrade", "Snapshot"]