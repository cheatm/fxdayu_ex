from fxdayu_ex.server.frame.engine import Consumer
from fxdayu_ex.module.account import AbstractAccount
from fxdayu_ex.server.frame.broker import Account
from fxdayu_ex.module.request import CancelOrder, ReqOrder, ReqSnapshot
from fxdayu_ex.module.storage import Order, Trade, Position, Cash, SnapShot
from fxdayu_ex.module.storage import BSType
from queue import Queue


class ClientInstance(Consumer, AbstractAccount):

    def __init__(self, accountID):
        super(ClientInstance, self).__init__(Queue(), 5)
        self.account = Account(accountID, None, {}, {})
        self.account.cancel_order()
        self.handlers = {
            Order.__name__: self.send_order,
            Trade.__name__: self.on_trade,
            SnapShot.__name__: self.on_snapshot
        }

        self.order_handler = {
            BSType.BUY.value: self.account.buy_order,
            BSType.SELL.value: self.account.sell_order
        }

        self.trade_handler = {
            BSType.BUY.value: self.account.buy_trade,
            BSType.SELL.value: self.account.sell_trade
        }

    def handle(self, quest):
        self.handlers[quest.__class__.__name__](quest)

    def send_order(self, order):
        self.order_handler[order.bsType](order)

    def on_trade(self, trade):
        self.trade_handler[trade.bsType](trade)

    def on_snapshot(self, snapshot):
        self.account._positions = snapshot.positions
        self.account._cash = snapshot.cash
        self.account._orders = snapshot.orders