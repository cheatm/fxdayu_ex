# encoding:utf-8
from fxdayu_ex.module.empty import *


class Cash:

    def __init__(self, available=EMPTY_FLOAT, freeze=EMPTY_FLOAT):
        self.available = available
        self.freeze = freeze


class Order:

    def __init__(self,
                 accountID=EMPTY_STR,
                 orderID=EMPTY_INT,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 cum_qty=EMPTY_INT,
                 price=EMPTY_FLOAT,
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
        self.fee = fee
        self.canceled = canceled
        self.status = status
        self.time = time
        self.cnfm_time = cnfm_time

    @property
    def unfilled(self):
        return self.qty - self.cum_qty


class Trade:

    def __init__(self,
                 accountID=EMPTY_STR,
                 orderID=EMPTY_INT,
                 tradeID=EMPTY_INT,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 price=EMPTY_FLOAT,
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
        self.fee = fee
        self.order_status = order_status
        self.time = time


class Position:

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


