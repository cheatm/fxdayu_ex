from fxdayu_ex.module.instance import Order, Trade, Cash, Position, SnapShot
from fxdayu_ex.module.enums import *
from fxdayu_ex.utils.json_adapt import JSONAdaptor


class Response(JSONAdaptor):

    INSTANCE = None

    @classmethod
    def from_instance(cls, instance):
        return cls(**instance.dict())

    def to_instance(self):
        return self.INSTANCE(**self.dict())


class RespOrder(Order, Response):

    INSTANCE = Order

    DIRECT = ("accountID", "orderID", "code", "qty", "cumQty", "price", "frzAmt",
              "frzFee", "cumAmt", "cumFee", "canceled", "time", "cnfmTime", "info")

    ENUMS = (("orderType", OrderType), ("bsType", BSType), ("orderStatus", OrderStatus), ("reason", CanceledReason))

    @classmethod
    def from_instance(cls, instance):
        return cls(**instance.dict())


class RespTrade(Trade, Response):

    INSTANCE = Trade

    DIRECT = ("accountID", "orderID", "tradeID", "code", "qty", "price", "fee", "time")

    ENUMS = ("orderType", "bsType", "orderStatus")

    @classmethod
    def from_instance(cls, instance):
        return cls(**instance.dict())


class RespCash(Cash, Response):

    INSTANCE = Cash

    DIRECT = Cash.__slots__

    @classmethod
    def from_instance(cls, instance):
        return cls(**instance.dict())


class RespPosition(Position, Response):

    DIRECT = Position.__slots__
    INSTANCE = Position

    @classmethod
    def from_instance(cls, instance):
        return cls(**instance.dict())
