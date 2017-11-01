from fxdayu_ex.server.frame.broker import Broker, Account
from fxdayu_ex.server.frame.exchange import Exchange, OrderPool, Transactor
from fxdayu_ex.server.frame.exceptions import *
from fxdayu_ex.server.frame.engine import Engine, TickEvent, ReqEvent, RespEvent
from fxdayu_ex.module.enums import OrderStatus, BSType, OrderType, CanceledReason
from fxdayu_ex.module.instance import Order, Trade, Cash, Position
from fxdayu_ex.module.request import ReqOrder, CancelOrder
import logging
from datetime import datetime


SO = "sell order"
BO = "buy order"
ST = "sell trade"
BT = "buy trade"
CO = "cancel order"
CSO = "cancel sell order"
CBO = "cancel buy order"


class Core(Engine):

    def __init__(self, exchange, broker, orderIDs, tradeIDs):
        super(Core, self).__init__()
        self.exchange = exchange
        self.broker = broker
        self.orderpool = exchange.pool
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

        self.handlers = {
            ReqEvent.type: self.handle_req,
            TickEvent.type: self.handle_tick
        }

    def handle_tick(self, event):
        self.on_tick(event.tick)

    def handle_req(self, event):
        req = event.req
        if isinstance(req, ReqOrder):
            self.on_req_order(req)
        elif isinstance(req, CancelOrder):
            self.on_cancel(req)

    def on_tick(self, tick):
        for trade in self.exchange.on_tick(tick):
            try:
                account = self.broker.account(trade.accountID)
            except AccountNotFound as e:
                logging.warning("AccountNotFound%s during transact", e)
            else:
                result = self.trade_handlers[trade.bsType.value](account, trade)
                if result is not None:
                    self.trade_success(trade)
                else:
                    self.trade_fail(trade)

    def on_buy_trade(self, account, trade):
        try:
            trade = account.buy_trade(trade)
        except OrderNotFound as e:
            logging.warning("OrderNotFound%s during %s: %s", e, BT, trade)
        except OrderTransactExceed as e:
            logging.warning("OrderTransactExceed%s during %s: %s, %s", e, BT, trade, account.get_order(trade.orderID))
        except CashUnfreezeExceed as e:
            logging.warning("CashUnfreezeExceed%s during %s: %s, %s, %s",
                            e, BT, account.cash, account.get_order(trade.orderID), trade)
        except CashSubExceed as e:
            logging.warning("CashSubExceed%s during %s: %s, %s, %s",
                            e, BT, account.cash, account.get_order(trade.orderID), trade)
        else:
            return trade

    def on_sell_trade(self, account, trade):
        try:
            trade = account.sell_trade(trade)
        except OrderNotFound as e:
            logging.warning("OrderNotFound%s during %s: %s", e, ST, trade)
        except OrderTransactExceed as e:
            logging.warning("OrderTransactExceed%s during %s: %s, %s", e, ST, trade, account.get_order(trade.orderID))
        except PositionNotFound as e:
            logging.warning("PositionNotFound%s during %s: %s", e, ST, trade)
        except PositionUnfreezeExceed as e:
            logging.warning("PositionUnfreezeExceed%s during %s: %s, %s", e, ST, trade, account.get_position(trade.code))
        else:
            self.put(ReqEvent(CancelOrder(trade.accountID, trade.orderID)))
            return trade

    def trade_fail(self, trade):
        logging.warning("%s fail", trade)

    def trade_success(self, trade):
        logging.info("%s success", trade)

    def on_req_order(self, req):
        order = self.create_order(req)
        if order is None:
            return

        try:
            account = self.broker.account(order.accountID)
        except AccountNotFound as e:
            logging.warning("AccountNotFound%s during req order: %s", e, req)
        else:
            self.order_handlers[order.bsType.value](account, order)
            logging.warning(str(account.cash))
        finally:
            self.save_req_order(req)

    def save_req_order(self, req):
        pass

    def create_order(self, req):
        if req.orderType.value == OrderType.LIMIT.value:
            return self._create_order(req)
        elif req.orderType.value == OrderType.MARKET.value:
            try:
                req.price = self.exchange.price_limit(req.code, req.bsType)
            except KeyError:
                self.snapshot_not_found(req)
            else:
                return self._create_order(req)

    def snapshot_not_found(self, req):
        logging.warning("Snapshot of %s not found", req.code)

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
                     time=req.time, cnfmTime=str(datetime.now()),
                     info=req.info)

    def on_buy_order(self, account, order):
        try:
            order = account.buy_order(order)
        except CashFreezeExceed as e:
            logging.warning("CashFreezeExceed(%s) during buy order: %s %s", e, account.cash, order)
            self._cancel(order, CanceledReason.CASH)
        else:
            self.buy_order_success(order, account.cash)

    def buy_order_success(self, order, cash):
        self.order_success(order)

    def on_sell_order(self, account, order):
        try:
            order = account.sell_order(order)
        except PositionNotFound as e:
            logging.warning("PositionNotFound(%s) during sell order: %s", e, order)
            self._cancel(order, CanceledReason.POSITION)
        except PositionFreezeExceed as e:
            logging.warning("PositionFreezeExceed(%s) during sell order: %s", e, order)
            self._cancel(order, CanceledReason.POSITION)
        else:
            self.sell_order_success(order, account.get_position(order.code))

    def sell_order_success(self, order, position):
        self.order_success(order)

    def order_success(self, order):
        if order.orderStatus.value == OrderStatus.UNFILLED.value:
            self.orderpool.put(order)
        return order

    def on_cancel(self, cancel):
        try:
            account = self.broker.account(cancel.accountID)
            order = account.get_order(cancel.orderID)
        except AccountNotFound as e:
            logging.warning("AccountNotFound%s during %s: %s", e, CO, cancel)
        except OrderNotFound as e:
            logging.warning("OrderNotFound%s during %s: %s", e, CO, cancel)
        else:
            order = self.cancel_handlers[order.bsType.value](account, cancel)
            if order is not None:
                self._cancel(order, CanceledReason.CLIENT)

    def cancel_sell(self, account, cancel):
        try:
            return account.cancel_sell(cancel.orderID)
        except PositionNotFound as e:
            logging.warning("PositionNotFound%s during %s: %s", e, CSO, cancel)
        except PositionUnfreezeExceed as e:
            logging.warning("PositionUnfreezeExceed%s during %s: %s", e, CSO, cancel)

    def cancel_buy(self, account, cancel):
        try:
            return account.cancel_buy(cancel.orderID)
        except CashUnfreezeExceed as e:
            logging.warning("CashUnfreezeExceed%s during %s: %s %s", e, CBO, cancel, account.cash)

    def _cancel(self, order, reason):
        canceled = order.unfilled
        order.canceled += canceled
        order.orderStatus = OrderStatus.CANCELED
        order.reason = reason
        return order


def simulation():
    accountID = 103

    tick = {'date': 20171018,
         'code': '300667.XSHE',
         'ask': [[464000, 2600], [464100, 600], [464200, 1300], [464300, 2900], [464400, 200]],
         'time': 94109000,
         'bid': [[463900, 200], [462900, 1000], [462800, 400], [462000, 300], [461900, 600]]}

    req = ReqOrder(accountID, '300667.XSHE', 3000, 464300, OrderType.LIMIT, BSType.BUY)
    req_sell = ReqOrder(accountID, "300667.XSHE", 1000, 463900, OrderType.LIMIT, BSType.SELL)

    frame = generate(accountID)
    frame.put(ReqEvent(req))
    frame.put(ReqEvent(req_sell))
    frame.put(TickEvent(tick))
    frame.start()

def generate(accountID):
    from fxdayu_ex.utils.id_generator import TimerIDGenerator
    from fxdayu_ex.utils.cal import Rate

    tradeIDs = TimerIDGenerator.year()
    orderIDs = TimerIDGenerator.year()
    pool = OrderPool()
    transactor = Transactor(tradeIDs, Rate(5, 10000), Rate(5, 10000))

    account = Account(accountID, Cash(accountID, 100000),
                      {"300667.XSHE": Position(accountID, "300667.XSHE", 3000, 3000)},
                      {})
    broker = Broker({accountID: account})
    frame = Core(Exchange(pool, transactor), broker, orderIDs, tradeIDs)
    return frame


if __name__ == '__main__':
    simulation()