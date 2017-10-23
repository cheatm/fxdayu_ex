# encoding:utf-8
from fxdayu_ex.module.empty import *


class ReqOrder:

    def __init__(self,
                 accountID=EMPTY_STR,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 price=EMPTY_FLOAT,
                 orderType=EMPTY,
                 bsType=EMPTY,
                 info=EMPTY_STR):
        self.accountID = accountID
        self.code = code
        self.qty = qty
        self.price = price
        self.orderType = orderType
        self.bsType = bsType
        self.info = info


class QryOrder:

    def __init__(self, accountID=EMPTY_STR, orderID=EMPTY_STR):
        self.accountID = accountID
        self.orderID = orderID


class CancelOrder:

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


class Snapshot:

    def __init__(self, accountID=EMPTY_STR):
        self.accountID = accountID


__all__ = ["ReqOrder", "CancelOrder", "QryOrder", "QryCash", "QryPosition", "QryTrade", "Snapshot"]