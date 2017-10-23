from fxdayu_ex.server.frame.broker import Broker
from fxdayu_ex.server.frame.exchange import Exchange, OrderPool
from fxdayu_ex.server.frame.exceptions import *
from fxdayu_ex.server.frame.engine import Engine, TickEvent, ReqEvent, RespEvent
from fxdayu_ex.module.enums import OrderStatus, BSType, OrderType
from fxdayu_ex.module.storage import Order, Trade, Cash, Position
from datetime import datetime



class FrameWork(Engine):

    def __init__(self, exchange, broker, orderpool, orderIDs, tradeIDs):
        super(FrameWork, self).__init__()
        self.exchange = exchange
        self.broker = broker
        self.orderpool = orderpool
        self.orderIDs = orderIDs
        self.tradeIDs = tradeIDs

        self.order_handlers = {
            BSType.BUY.value: self.on_buy_order,
            BSType.SELL.value: self.on_sell_order,
        }

        self.trade_handlers = {
            BSType.BUY.value: self.on_buy_trade,
            BSType.SELL.value: self.on_sell_trade,
        }

        self.cancel_handlers = {
            BSType.BUY.value: self.cancel_buy,
            BSType.SELL.value: self.cancel_sell,
        }

        self.fee_rate = {
            BSType.BUY.value: exchange.transactor.br,
            BSType.SELL.value: exchange.transactor.sr,
        }

    def on_tick(self, tick):
        for trade in self.exchange.on_tick(tick):
            try:
                account = self.broker.account(trade.accountID)
            except AccountNotFound:
                pass
            else:
                self.trade_handlers[trade.bsType.value](account, trade)

            yield trade

    def on_buy_trade(self, account, trade):
        try:
            trade, order, cash, position = account.buy_trade(trade)
        except OrderNotFound:
            pass
        except OrderTransactExceed:
            pass
        except CashUnfreezeExceed:
            pass
        except CashSubExceed:
            pass
        else:
            self.buy_trade_success(trade, order, cash, position)

    def buy_trade_success(self, trade, order, cash, position):
        pass

    def on_sell_trade(self, account, trade):
        try:
            trade, order, cash, position = account.sell_trade(trade)
        except OrderNotFound:
            pass
        except OrderTransactExceed:
            pass
        except PositionNotFound:
            pass
        except PositionUnfreezeExceed:
            pass
        else:
            self.sell_trade_success(trade, order, cash, position)

    def sell_trade_success(self, trade, order, cash, position):
        pass

    def on_req_order(self, req):
        order = self.create_order(req)
        if order is None:
            return

        try:
            account = self.broker.account(order.accountID)
        except AccountNotFound:
            pass
        else:
            self.order_handlers[order.bsType.value](account, order)

    def create_order(self, req):
        if req.orderType.value == OrderType.LIMIT:
            self._create_order(req)
        elif req.orderType.value == OrderType.MARKET:
            try:
                req.price = self.exchange.price_limit(req.code, req.bsType)
            except KeyError:
                self.listen(req.code)
                self.put(ReqEvent(req))
                return None
            else:
                return self._create_order(req)

    def listen(self, code):
        pass

    def _create_order(self, req):

        if req.bsType.value == BSType.BUY.value:
            frzAmt = req.price*req.qty
            frzFee = self.exchange.transactor.br*frzAmt
        else:
            frzAmt, frzFee = 0, 0

        return Order(req.accountID, self.orderIDs.next(),
                     req.code, req.qty,
                     price=req.price, bsType=req.bsType,
                     frzAmt=frzAmt, frzFee=frzFee,
                     time=req.time, cnfmTime=datetime.now())

    def on_buy_order(self, account, order):
        try:
            order = account.buy_order(order)
        except CashFreezeExceed:
            pass
        else:
            self.buy_order_success(order, account.cash)

    def buy_order_success(self, order, cash):
        self.on_order(order)

    def on_sell_order(self, account, order):
        try:
            order = account.sell_order(order)
        except PositionNotFound:
            pass
        except PositionFreezeExceed:
            pass
        else:
            self.sell_order_success(order, account.get_position(order.code))

    def sell_order_success(self, order, position):
        self.on_order(order)

    def on_order(self, order):
        if order.status.value == OrderStatus.UNFILLED.value:
            self.orderpool.put(order)
        return order

    def on_cancel(self, cancel):
        try:
            account = self.broker.account(cancel.accountID)
            order = account.get_order(cancel.orderID)
        except AccountNotFound:
            pass
        except OrderNotFound:
            pass
        else:
            return self.cancel_handlers[order.bsType.value](account, cancel)

    def cancel_sell(self, account, cancel):
        try:
            return account.cancel_buy(cancel.orderID)
        except PositionNotFound:
            pass
        except PositionUnfreezeExceed:
            pass

    def cancel_buy(self, account, cancel):
        try:
            return account.cancel_buy(cancel.orderID)
        except CashUnfreezeExceed:
            pass

    """------------------------------------------Exception Handlers------------------------------------------"""

    def account_not_found(self, e, process=""):
        print("During", process, "Account(%s) not found" % e.accountID)

    def order_not_found(self, e, process=""):
        print("During", process, "Order(accountID=%s, orderID=%s) not found" % (e.accountID, e.orderID))

    def position_not_found(self, e, process=""):
        print("During", process, "Position(accountID=%s, code=%s) not found" % (e.accountID, e.code))

    def position_unfreeze_exceed(self, e, process=""):
        PositionUnfreezeExceed.
        print("During", process, ""