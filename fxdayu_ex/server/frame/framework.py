from fxdayu_ex.server.frame.broker import Broker, Account
from fxdayu_ex.server.frame.exchange import Exchange, OrderPool, Transactor
from fxdayu_ex.server.frame.exceptions import *
from fxdayu_ex.server.frame.engine import Engine, TickEvent, ReqEvent, RespEvent
from fxdayu_ex.module.enums import OrderStatus, BSType, OrderType, CanceledReason
from fxdayu_ex.module.storage import Order, Trade, Cash, Position
from fxdayu_ex.module.request import ReqOrder, CancelOrder
from datetime import datetime


SO = "sell order"
BO = "buy order"
ST = "sell trade"
BT = "buy trade"
CO = "cancel order"
CSO = "cancel sell order"
CBO = "cancel buy order"


class FrameWork(Engine):

    def __init__(self, exchange, broker, orderIDs, tradeIDs):
        super(FrameWork, self).__init__()
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
                self.account_not_found(e, "transact trade")
            else:
                result = self.trade_handlers[trade.bsType.value](account, trade)
                if result is not None:
                    self.trade_success(trade)
                else:
                    self.trade_fail(trade)

    def on_buy_trade(self, account, trade):
        try:
            trade= account.buy_trade(trade)
        except OrderNotFound as e:
            self.order_not_found(e, BT)
        except OrderTransactExceed as e:
            self.order_transact_exceed(e, BT)
        except CashUnfreezeExceed as e:
            self.cash_unfreeze_exceed(e, BT)
        except CashSubExceed as e:
            self.cash_sub_exceed(e, BT)
        else:
            print(account.get_order(trade.orderID))
            return trade

    def on_sell_trade(self, account, trade):
        try:
            trade = account.sell_trade(trade)
        except OrderNotFound as e:
            self.order_not_found(e, ST)
        except OrderTransactExceed as e:
            self.order_transact_exceed(e, ST)
        except PositionNotFound as e:
            self.position_not_found(e, ST)
        except PositionUnfreezeExceed as e:
            self.position_unfreeze_exceed(e, ST)
        else:
            print(account.cash)
            print(account.get_position(trade.code))
            self.put(ReqEvent(CancelOrder(trade.accountID, trade.orderID)))
            return trade

    def trade_fail(self, trade):
        print("fail", trade)

    def trade_success(self, trade):
        print("success", trade)

    def on_req_order(self, req):
        order = self.create_order(req)
        print(order)
        if order is None:
            return

        try:
            account = self.broker.account(order.accountID)
        except AccountNotFound as e:
            self.account_not_found(e, "ReqOrder")
        else:
            self.order_handlers[order.bsType.value](account, order)

    def create_order(self, req):
        if req.orderType.value == OrderType.LIMIT.value:
            return self._create_order(req)
        elif req.orderType.value == OrderType.MARKET.value:
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
        except CashFreezeExceed as e:
            self.cash_freeze_exceed(e, BO)
            self._cancel(order, CanceledReason.CASH)
        else:
            self.buy_order_success(order, account.cash)

    def buy_order_success(self, order, cash):
        self.on_order(order)
        print(cash)

    def on_sell_order(self, account, order):
        try:
            order = account.sell_order(order)
        except PositionNotFound as e:
            self.position_not_found(e, SO)
            self._cancel(order, CanceledReason.POSITION)
        except PositionFreezeExceed as e:
            self.position_freeze_exceed(e, SO)
            self._cancel(order, CanceledReason.POSITION)
        else:
            self.sell_order_success(order, account.get_position(order.code))

    def sell_order_success(self, order, position):
        self.on_order(order)

    def on_order(self, order):
        if order.status.value == OrderStatus.UNFILLED.value:
            self.orderpool.put(order)
        self.listen(order.code)
        return order

    def on_cancel(self, cancel):
        try:
            account = self.broker.account(cancel.accountID)
            order = account.get_order(cancel.orderID)
        except AccountNotFound as e:
            self.account_not_found(e, CO)
        except OrderNotFound as e:
            self.order_not_found(e, CO)
        else:
            order = self.cancel_handlers[order.bsType.value](account, cancel)
            if order is not None:
                self._cancel(order, CanceledReason.CLIENT)
                print(order)
                print(account.cash)

    def cancel_sell(self, account, cancel):
        try:
            return account.cancel_buy(cancel.orderID)
        except PositionNotFound as e:
            self.position_not_found(e, CSO)
        except PositionUnfreezeExceed as e:
            self.position_unfreeze_exceed(e, CSO)

    def cancel_buy(self, account, cancel):
        try:
            return account.cancel_buy(cancel.orderID)
        except CashUnfreezeExceed as e:
            self.cash_unfreeze_exceed(e, CBO)

    def _cancel(self, order, reason):
        canceled = order.unfilled
        order.canceled += canceled
        order.status = OrderStatus.CANCELED
        order.reason = reason
        return order

    """------------------------------------------Exception Handlers------------------------------------------"""

    def exception_output(self, process, name, end="", **kwargs):
        print("During", process, self.simple_output(name, **kwargs), end)

    @staticmethod
    def simple_output(name, **kwargs):
        return "%s(%s)" % (name, ', '.join(["%s=%s" % (key, value) for key, value in kwargs.items()]))

    def account_not_found(self, e, process=""):
        self.exception_output(process, "Account", "not found", accountID=e.accountID)

    def order_not_found(self, e, process=""):
        self.exception_output(process, "Order", accountID=e.accountID, orderID=e.orderID)

    def position_not_found(self, e, process=""):
        self.exception_output(process, "Position", accountID=e.accountID, code=e.code)

    def position_unfreeze_exceed(self, e, process=""):
        self.exception_output(process, "Position", e.qty, accountID=e.accountID, code=e.code, frozen=e.frozen)

    def position_freeze_exceed(self, e, process=""):
        self.exception_output(process, "Position", e.qty, accountID=e.accountID, code=e.code, available=e.available)

    def cash_freeze_exceed(self, e, process=""):
        self.exception_output(process, "Cash", e.freeze, accountID=e.accountID, available=e.available)

    def cash_unfreeze_exceed(self, e, process=""):
        self.exception_output(process, "Cash", e.unfreeze, accountID=e.accountID, frozen=e.frozen)

    def cash_sub_exceed(self, e, process=""):
        self.exception_output(process, "Cash", e.sub, accountID=e.accountID, frozen=e.frozen)

    def order_transact_exceed(self, e, process=""):
        order = e.order
        trade = e.trade
        print("During", process, str(trade), "->", str(order), "exceed")


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

    account = Account(accountID, Cash(accountID, 100000000000),
                      {"300667.XSHE": Position(accountID, "300667.XSHE", 3000, 3000)},
                      {})
    broker = Broker({accountID: account})
    frame = FrameWork(Exchange(pool, transactor), broker, orderIDs, tradeIDs)
    return frame


if __name__ == '__main__':
    simulation()