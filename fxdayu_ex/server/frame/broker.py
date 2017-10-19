# encoding:utf-8
from fxdayu_ex.module.storage import Order, Trade, Cash, Position
from fxdayu_ex.module.request import *
from fxdayu_ex.module.account import AbstractAccount
from fxdayu_ex.module.enums import OrderStatus


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
        if isinstance(qry_trade, QryTrade):
            return self.account(qry_trade.accountID).get_trade(qry_trade.orderID)

    def get_position(self, qry_position):
        if isinstance(qry_position, QryPosition):
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

    def __init__(self, cash, positions, orders, id):
        self._cash = cash
        self._positions = positions
        self._orders = orders
        self._id = id

    def send_order(self, order):
        return Order()

    def cancel_order(self, orderID):
        return Order()

    def get_order(self, orderID):
        return Order()

    def get_position(self, code):
        return Position()

    def transaction(self, trade):
        pass

    def get_trade(self, orderID):
        return Trade

    @property
    def cash(self):
        return self._cash

    @property
    def positions(self):
        return self._positions.copy()

    @property
    def orders(self):
        return self._orders.copy()