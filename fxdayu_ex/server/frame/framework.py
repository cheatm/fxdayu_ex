from fxdayu_ex.server.frame.broker import Broker
from fxdayu_ex.server.frame.exchange import Exchange, OrderPool
from fxdayu_ex.server.frame.exceptions import *
from fxdayu_ex.server.frame.engine import Engine, TickEvent, ReqEvent, RespEvent
from fxdayu_ex.module.enums import OrderStatus
from fxdayu_ex.module.storage import Order, Trade, Cash, Position



class FrameWork(Engine):

    def __init__(self, exchange, broker, orderpool):
        super(FrameWork, self).__init__()
        self.exchange = exchange
        self.broker = broker
        self.orderpool = orderpool

    def on_tick(self, tick):
        for trade in self.exchange.on_tick(tick):
            self.broker.trade(trade)
            yield trade

    def on_order(self, order):
        order = self.broker.order(order)
        if order.status.value == OrderStatus.UNFILLED.value:
            self.orderpool.put(order)
        return order

    def on_cancel(self, cancel):
        order = self.broker.cancel(cancel)
        if order.status.value == OrderStatus.CANCELED.value:
            self.orderpool.cancel(order)
        return order

