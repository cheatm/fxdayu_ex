# encoding:utf-8
from fxdayu_ex.module.empty import *

class Structure:

    __slots__ = []

    def __str__(self):
        return "{}({})" .format(
            self.__class__.__name__,
            ', '.join(["{}={}".format(attr, self.__getattribute__(attr)) for attr in self.__slots__])
        )


class Cash(Structure):

    __slots__ = ["available", "freeze"]

    def __init__(self, available=EMPTY_FLOAT, freeze=EMPTY_FLOAT):
        self.available = available
        self.freeze = freeze



class Order(Structure):

    __slots__ = ["accountID", "orderID", "code", "qty", "cum_qty", "price", "order_type", "bs_type", "fee",
                 "canceled", "status", "time", "cnfm_time"]

    def __init__(self,
                 accountID=EMPTY_STR,
                 orderID=EMPTY_INT,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 cum_qty=EMPTY_INT,
                 price=EMPTY_FLOAT,
                 order_type=EMPTY_INT,
                 bs_type=EMPTY_INT,
                 fee=EMPTY_FLOAT,
                 canceled=EMPTY_INT,
                 status=EMPTY_INT,
                 time=EMPTY,
                 cnfm_time=EMPTY):
        self.accountID = accountID
        self.orderID = orderID
        self.code = code
        self.qty = qty
        self.cum_qty = cum_qty
        self.price = price
        self.order_type = order_type
        self.bs_type = bs_type
        self.fee = fee
        self.canceled = canceled
        self.status = status
        self.time = time
        self.cnfm_time = cnfm_time

    @property
    def unfilled(self):
        return self.qty - self.cum_qty - self.canceled


class Trade(Structure):
    __slots__ = ["accountID", "orderID", "tradeID", "code", "qty", "price", "order_type", "bs_type", "fee",
                 "order_status", "time"]

    def __init__(self,
                 accountID=EMPTY_STR,
                 orderID=EMPTY_INT,
                 tradeID=EMPTY_INT,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 price=EMPTY_FLOAT,
                 order_type=EMPTY_INT,
                 bs_type=EMPTY_INT,
                 fee=EMPTY_FLOAT,
                 order_status=EMPTY_INT,
                 time=EMPTY
                 ):
        self.accountID = accountID
        self.orderID = orderID
        self.tradeID = tradeID
        self.code = code
        self.qty = qty
        self.price = price
        self.order_type = order_type
        self.bs_type = bs_type
        self.fee = fee
        self.order_status = order_status
        self.time = time

    def __eq__(self, other):
        return self.accountID == other.accountID


class Position(Structure):

    __slots__ = ["accountID", "code", "origin", "available", "today", "today_sell"]

    def __init__(self,
                 accountID=EMPTY_STR,
                 code=EMPTY_STR,
                 origin=EMPTY_INT,
                 available=EMPTY_INT,
                 today=EMPTY_INT,
                 today_sell=EMPTY_INT,
                 ):
        self.accountID = accountID
        self.code = code
        self.origin = origin
        self.available = available
        self.today = today
        self.today_sell = today_sell


if __name__ == '__main__':
    print(Position())
