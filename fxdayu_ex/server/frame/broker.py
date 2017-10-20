# encoding:utf-8
from fxdayu_ex.module.enums import OrderStatus, BSType, CanceledReason, OrderType
from fxdayu_ex.module.storage import Order, Trade, Cash, Position
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

        self.oh = {
            BSType.BUY.value: self.buy_order,
            BSType.SELL.value: self.sell_order
        }

        self.th = {
            BSType.BUY.value: self.buy_trade,
            BSType.SELL.value: self.sell_trade
        }

    def send_order(self, order):
        return self.oh[order.bsType.value](order)

    def buy_order(self, order):
        frz = order.frzAmt + order.frzFee
        self._cash.freeze(frz)
        self._orders[order.orderID] = order
        order.status = OrderStatus.UNFILLED
        return order

    def sell_order(self, order):
        position = self.get_position(order.code)
        position.freeze(order.qty)
        order.status = OrderStatus.UNFILLED
        return order

    @staticmethod
    def _cancel(order, reason, qty):
        order.status = OrderStatus.CANCELED
        order.reason = reason
        order.canceled = qty
        return order

    def cancel_order(self, orderID):
        order = self._orders.pop(orderID, None)
        if order is not None:
            return self._cancel(order, CanceledReason.CLIENT, order.unfilled)
        else:
            return None

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

    def transaction(self, trade):
        return self.th[trade.bsType.value](trade)

    def buy_trade(self, trade):
        # order = self.get_order(trade.orderID)
        # fee = trade.fee
        # amt = trade.qty * trade.price
        # self._cash.sub(fee + amt)
        # cumQty = order.cumQty + trade.qty
        # cumFee = order.cumFee + fee
        # cumAmt = order.cumAmt + amt
        #
        # if order.unfilled == 0:
        #     self._cash.unfreeze(order.frzFee+order.frzAmt-cumAmt-cumFee)
        #     order.cumFee = cumFee
        #     self.order_accomplish(order, trade)
        #
        # if trade.code in self._positions:
        #     position = self._positions[trade.code]
        #     position.add(trade.qty)
        # else:
        #     position = Position(self.accountID, trade.code, today=trade.qty)
        #     self._positions[trade.code] = position

        return trade

    def sell_trade(self, trade):
        order = self.get_order(trade.orderID)
        position = self.get_position(trade.code)
        position.sub(trade.qty)
        self._cash.add(trade.qty*trade.price-trade.fee)
        order.cumQty += trade.qty
        order.cumFee += trade.fee
        if order.unfilled == 0:
            self.order_accomplish(order, trade)
        return trade

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


class PositionNotFound(Exception):

    def __init__(self, accountID, code):
        self.accountID = accountID
        self.code = code


def acc_t():
    id = 0
    order = Order(id, 111, "000001.XSHE", 1000, 0, 12.5, OrderType.LIMIT, BSType.BUY)
    account = Account(id, Cash(100000000), {}, {})
    account.send_order(order)
    print(account.get_order(111))
    print(account.cash)
    trade = Trade(id, 111, 222, "000001.XSHE", 500, 12.5, OrderType.LIMIT, BSType.BUY, 5, OrderStatus.UNFILLED)
    account.transaction(trade)
    print(account.cash)
    print(account.get_position("000001.XSHE"))


if __name__ == '__main__':
    acc_t()