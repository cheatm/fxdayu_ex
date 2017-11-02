from fxdayu_ex.module.instance import Cash, Order, Position, Trade
from fxdayu_ex.module.enums import OrderType, BSType, OrderStatus, CanceledReason
from fxdayu_ex.utils.json_adapt import DictNoCls


class OrderRecord(Order, DictNoCls):

    DIRECT = ("accountID", "orderID", "code", "qty", "cumQty", "price", "frzAmt",
              "frzFee", "cumAmt", "cumFee", "canceled", "time", "cnfmTime", "info")
    ENUMS = (("orderType", OrderType), ("bsType", BSType), ("orderStatus", OrderStatus), ("reason", CanceledReason))


class TradeRecord(Trade, DictNoCls):

    DIRECT = ("accountID", "orderID", "tradeID", "code", "qty", "price", "fee", "time")

    ENUMS = (("orderType", OrderType), ("bsType", BSType), ("orderStatus", OrderStatus))


class PositionRecord(Position, DictNoCls):

    DIRECT = Position.__slots__


class CashRecord(Cash, DictNoCls):

    DIRECT = Cash.__slots__