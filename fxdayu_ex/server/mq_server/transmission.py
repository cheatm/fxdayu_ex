from itertools import chain
from fxdayu_ex.module.enums import BSType, OrderType, CanceledReason, OrderStatus
from fxdayu_ex.module.request import ReqOrder, CancelOrder
from fxdayu_ex.module.storage import Cash, Order, Trade, Position


def dct2obj(cls, directs, funcs):
    def obj(dct):
        return cls(**dict(chain(
            ((name, dct[name]) for name in directs),
            ((name, func(dct[name])) for name, func in funcs)
        )))

    return obj


def obj2dct(directs, funcs):
    def dct(obj):
        return dict(chain(
            ((name, getattr(obj, name)) for name in directs),
            ((name, func(getattr(obj, name))) for name, func in funcs),
        ))
    return dct


def enum_value(ens):
    return ens.value


ACCOUNT_ID = "accountID"
ORDER_ID = "orderID"
CODE = "code"
QTY = "qty"
PRICE = "price"
TIME = "time"
INFO = "info"
AVL = "available"
FRZ = "frozen"

ORD_TYPE = "orderType"
ORD_TYPE_VALUE = (ORD_TYPE, enum_value)
ORD_TYPE_ENUM = (ORD_TYPE, OrderType)

BS_TYPE = "bsType"
DUMP_BS_TYPE = (BS_TYPE, enum_value)
LOAD_BS_TYPE = (BS_TYPE, BSType)

REASON = "reason"
REASON_VALUE = (REASON, enum_value)
REASON_ENUM = (REASON, CanceledReason)

STATUS = "orderStatus"
STATUS_VALUE = (STATUS, enum_value)
STATUS_ENUM = (STATUS, OrderStatus)

# RecOrder
ro_direct = (ACCOUNT_ID, CODE, QTY, PRICE, TIME, INFO)
load_req = dct2obj(ReqOrder, ro_direct, (LOAD_BS_TYPE, ORD_TYPE_ENUM))
dump_req = obj2dct(ro_direct, (DUMP_BS_TYPE, ORD_TYPE_VALUE))


# CancelOrder
load_cancel = dct2obj(CancelOrder, (ACCOUNT_ID, ORDER_ID), ())
dump_cancel = obj2dct((ACCOUNT_ID, ORDER_ID), ())


# Cash
CASH = (ACCOUNT_ID, AVL, FRZ)

load_cash = dct2obj(Cash, CASH, ())
dump_cash = obj2dct(CASH, ())


# Order
ORDER = ("accountID", "orderID", "code", "qty", "cumQty", "price", "frzAmt",
         "frzFee", "cumAmt", "cumFee",  "canceled", "time", "cnfmTime")
load_order = dct2obj(Order, ORDER, (ORD_TYPE_ENUM, LOAD_BS_TYPE, STATUS_ENUM, REASON_ENUM))
dump_order = obj2dct(ORDER, (ORD_TYPE_VALUE, DUMP_BS_TYPE, STATUS_VALUE, REASON_VALUE))


# Trade
TRADE = ["accountID", "orderID", "tradeID", "code", "qty", "price", "fee", "time"]
load_trade = dct2obj(Trade, TRADE, (ORD_TYPE_ENUM, LOAD_BS_TYPE, STATUS_ENUM))
dump_trade = obj2dct(TRADE, (ORD_TYPE_VALUE, DUMP_BS_TYPE, STATUS_VALUE))


# Position
POSITION = ["accountID", "code", "origin", "available", "frozen", "today", "todaySell"]
load_position = dct2obj(Position, POSITION, ())
dump_position = obj2dct(POSITION, ())
