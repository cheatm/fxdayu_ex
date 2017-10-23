# encoding:utf-8
from fxdayu_ex.module.enums import OrderStatus, BSType, CanceledReason, OrderType
from fxdayu_ex.module.storage import Order, Trade, Cash, Position, CashUnfreezeExceed, CashSubExceed, PositionSubExceed
from fxdayu_ex.module.request import *
from fxdayu_ex.module.account import AbstractAccount


class Broker(object):

    def __init__(self, accounts=None, pool=None):
        self.accounts = accounts if accounts is not None else dict()
        self.pool = pool

    # Need to be re write !!!
    def account(self, accountID):
        """Get account instance from accountID"""
        return self.accounts[accountID]

    def order(self, order):
        order = self.account(order.accountID).send_order(order)
        if order.status.value == OrderStatus.UNFILLED.value:
            self.pool.put(order)

        return order

    def cancel(self, cancel):
        order = self.account(cancel.accountID).cancel_order(cancel.orderID)
        if order.status.value == OrderStatus.CANCELED.value:
            pass

    def trade(self, trade):
        if isinstance(trade, Trade):
            self.account(trade.accountID).transaction(trade)
            return trade

    def get_order(self, qry_order):
        if isinstance(qry_order, QryOrder):
            return self.account(qry_order.accountID).get_order(qry_order.orderID)

    def get_trade(self, qry_trade):
        return self.account(qry_trade.accountID).get_trade(qry_trade.orderID)

    def get_position(self, qry_position):
        return self.account(qry_position.accountID).get_position(qry_position.code)

    def cash(self, accountID):
        return self.account(accountID).cash

    def snapshot(self, accountID):
        account = self.account(accountID)
        return {
            "cash": account.cash,
            "position": account.positions,
            "order": account.pack
        }


class Account(AbstractAccount):

    def __init__(self, accountID, cash, positions, orders):
        self.accountID = accountID
        self._cash = cash
        self._positions = positions
        self._orders = orders

    def send_order(self, order):
        pass

    def buy_order(self, order):
        frz = order.frzAmt + order.frzFee
        self._cash.freeze(frz)
        self._orders[order.orderID] = order
        order.status = OrderStatus.UNFILLED
        return order

    def sell_order(self, order):
        position = self.get_position(order.code)
        position.freeze(order.qty)
        self._orders[order.orderID] = order
        order.status = OrderStatus.UNFILLED
        return order

    @staticmethod
    def _cancel(order, reason, qty):
        order.status = OrderStatus.CANCELED
        order.reason = reason
        order.canceled = qty
        return order

    def cancel_order(self, orderID):
        order = self._orders.get(orderID, None)
        if order is not None:
            return self._cancel(order, CanceledReason.CLIENT, order.unfilled)
        else:
            return None

    def cancel_buy(self, orderID):
        order = self.get_order(orderID)
        self._cash.unfreeze(order.frzFee+order.frzAmt-order.cumAmt-order.cumFee)
        self._cancel(order, CanceledReason.CLIENT, order.unfilled)
        return self._orders.pop(order.orderID)

    def cancel_sell(self, orderID):
        order = self.get_order(orderID)
        position = self.get_position(order.code)
        position.unfreeze(order.unfilled)
        self._cancel(order, CanceledReason.CLIENT, order.unfilled)
        return self._orders.pop(order.orderID)

    def get_order(self, orderID):
        if orderID in self._orders:
            return self._orders[orderID]
        else:
            raise OrderNotFound(self.accountID, orderID)

    def get_position(self, code):
        if code in self._positions:
            return self._positions[code]
        else:
            raise PositionNotFound(self.accountID, code)

    def buy_trade(self, trade):
        order = self.get_order(trade.orderID)
        self._atomic_buy(order, trade)
        try:
            position = self._positions[trade.code]
        except KeyError:
            position = Position(self.accountID, trade.code)
            self._positions[trade.code] = position

        position.add(trade.qty)

        return trade, order, self._cash, position

    def _atomic_buy(self, order, trade):
        cumQty = order.cumQty + trade.qty
        cumFee = order.cumFee + trade.fee
        cumAmt = order.cumAmt + trade.qty * trade.price
        if (cumQty + order.canceled > order.qty) or (cumFee > order.frzFee) or (cumAmt > order.frzAmt):
            raise OrderTransactExceed(order, trade)

        frozen = self._cash.frozen - trade.qty * trade.price - trade.fee
        if frozen < 0:
            raise CashSubExceed(self.cash.available, self.cash.frozen, trade.qty * trade.price + trade.fee)

        if cumQty + order.canceled == order.qty:
            extra = order.frzAmt + order.frzFee - cumFee - cumAmt
            frozen -= extra
            if frozen < 0:
                raise CashUnfreezeExceed(frozen + extra, extra)
            else:
                self.order_accomplish(order, trade)
                self._cash.available += extra

        order.cumFee = cumFee
        order.cumAmt = cumAmt
        order.cumQty = cumQty
        self._cash.frozen = frozen

    def sell_trade(self, trade):
        order = self.get_order(trade.orderID)
        position = self.get_position(trade.code)
        self._atomic_sell(order, trade, position)
        return trade, order, self._cash, position

    def _atomic_sell(self, order, trade, position):
        cumAmt = order.cumAmt + trade.qty*trade.price
        cumFee = order.cumFee + trade.fee
        cumQty = order.cumQty + trade.qty
        if cumQty + order.canceled > order.qty:
            raise OrderTransactExceed(order, trade)

        position.sub(trade.qty)

        if cumQty + order.canceled == order.qty:
            self.order_accomplish(order, trade)

        order.cumFee = cumFee
        order.cumAmt = cumAmt
        order.cumQty = cumQty
        self._cash.add(trade.qty*trade.price-trade.fee)

    def order_accomplish(self, order, trade):
        order.status = OrderStatus.FILLED
        trade.orderStatus = order.status
        self._orders.__delitem__(order.orderID)

    def get_trade(self, orderID):
        return Trade()

    @property
    def cash(self):
        return self._cash

    @property
    def positions(self):
        return self._positions.copy()

    @property
    def orders(self):
        return self._orders.copy()


class OrderNotFound(Exception):

    def __init__(self, accountID, orderID):
        self.accountID = accountID
        self.orderID = orderID


class AccountNotFound(Exception):

    def __init__(self, accountID):
        self.accountID = accountID


class TradeNotFound(Exception):

    def __init__(self, accountID, orderID, tradeID):
        self.accountID = accountID
        self.orderID = orderID
        self.tradeID = tradeID


class TransactExceed(Exception):

    def __init__(self, order, trade):
        self.order = order
        self.trade = trade


class PositionNotFound(Exception):

    def __init__(self, accountID, code):
        self.accountID = accountID
        self.code = code


class OrderTransactExceed(Exception):

    def __init__(self, order, trade):
        self.order = order
        self.trade = trade


def acc_t():
    id = 0
    code = "000001.XSHE"
    order = Order(id, 111, "000001.XSHE", 1000, 0, 12.5, OrderType.LIMIT, BSType.SELL, frzAmt=1000*12.5, frzFee=20)
    account = Account(id, Cash(10000), {}, {})
    try:
        account.send_order(order)
    except Exception as e:
        print(e)

    print(account.orders)
    # trade = Trade(id, 111, 222, "000001.XSHE", 600, 12.5, OrderType.LIMIT, BSType.BUY, 5, OrderStatus.UNFILLED)
    # account.transaction(trade)
    # account.transaction(trade)



if __name__ == '__main__':
    acc_t()