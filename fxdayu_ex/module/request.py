# encoding:utf-8
from fxdayu_ex.module.empty import *


class OrderBook:

    def __init__(self,
                 accountID=EMPTY_STR,
                 code=EMPTY_STR,
                 quantity=EMPTY_INT,
                 price=EMPTY_FLOAT,
                 order_type=EMPTY_STR,
                 bs_type=EMPTY_STR,
                 info=EMPTY_STR):
        self.accountID = accountID
        self.code = code
        self.quantity = quantity
        self.price = price
        self.order_type = order_type
        self.bs_type = bs_type
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


__all__ = ["OrderBook", "CancelOrder", "QryOrder", "QryCash", "QryPosition", "QryTrade", "Snapshot"]