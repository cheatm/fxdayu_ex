from fxdayu_ex.utils.mysql import *
from fxdayu_ex.server.frame.engine import Consumer
from fxdayu_ex.module.record import Cash, CashRecord, Order, OrderRecord, Trade, TradeRecord, Position, PositionRecord
from fxdayu_ex.server.frame.broker import Account
from datetime import date
from queue import Queue
import logging


class MysqlEngine(Consumer):

    def __init__(self, url):
        super(MysqlEngine, self).__init__(Queue(), 5)
        try:
            self.parser = MysqlURLParser(url)
        except Exception as e:
            raise Exception("Parse mysql url: %s fail: %s" % (url, e))
        self.connection = self.parser.connect()
        self._accounts = AccountTable()

        self.tables = {
            CashRecord.__name__: CashTable(),
            OrderRecord.__name__: OrderTable(),
            TradeRecord.__name__: TradeTable(),
            PositionRecord.__name__: PositionTable()
        }

    def buy_order(self, order, cash):
        self.queue.put(
            (CashRecord(**cash.dict()),
             OrderRecord(**order.dict()))
        )

    def sell_order(self, order, position):
        self.queue.put(
            (PositionRecord(**position.dict()),
             OrderRecord(**order.dict()))
        )

    def trade(self, cash, order, trade, position):
        self.queue.put((CashRecord(**cash.dict()),
                        OrderRecord(**order.dict()),
                        TradeRecord(**trade.dict()),
                        PositionRecord(**position.dict())))

    def buy_cancel(self, order, cash):
        self.queue.put((CashRecord(**cash.dict()),
                        OrderRecord(**order.dict())))

    def sell_cancel(self, order, position):
        self.queue.put(PositionRecord(**position.dict()),
                       OrderRecord(**order.dict()))

    def handle(self, quest):
        cursor = self.connection.cursor()
        for record in quest:
            table = self.tables[record.__class__.__name__]
            try:
                self.update(table, record, cursor)
            except MysqlNothingChanged:
                try:
                    logging.warning("Update changed 0: %s", record)
                    self.insert(table, record, cursor)
                except Exception as e:
                    self.connection.rollback()
                    logging.error("Insert %s fail: %s", record, e)
                    return
            except Exception as e:
                self.connection.rollback()
                logging.error("Update %s fail: %s", record, e)
                return

        self.connection.commit()

    @staticmethod
    def insert(table, record, cursor):
        cursor.execute(table.insert(record))
        logging.info("Insert: %s", record)

    @staticmethod
    def update(table, record, cursor):
        changed = cursor.execute(table.update(record))
        if changed == 0:
            raise MysqlNothingChanged()

    def accountIDs(self):
        cursor = self.connection.cursor()
        cursor.execute(self._accounts.select("accountID", "active=1"))
        return [result[0] for result in cursor.fetchall()]

    def accounts(self):
        return dict(self.iter_accounts())

    def iter_accounts(self):
        for accountID in self.accountIDs():
            try:
                account = self.generate(accountID)
            except Exception as e:
                logging.error("Load account: %s fail: %s", accountID, e)
            else:
                yield accountID, account

    def generate(self, accountID):
        return Account(accountID,
                       self._cash(accountID),
                       self._positions(accountID),
                       self._orders(accountID))

    def _orders(self, accountID):
        cursor = self.connection.cursor()
        self._select(cursor, OrderRecord, Order,
                     ("accountID=%s" % accountID,
                      "time>'%s'" % today()))

        orders = {}
        for result in cursor.fetchall():
            order = Order(*result)
            orders[order.orderID] = order

        return orders

    def _trades(self, accountID):
        cursor = self.connection.cursor()
        self._select(cursor, TradeRecord, Trade,
                     ("accountID=%s" % accountID,
                      "time>'%s'" % today()))

        trades = {}
        for result in cursor.fetchall():
            trade = Trade(*result)
            trades[trade.tradeID] = trade

        return trades

    def _positions(self, accountID):
        cursor = self.connection.cursor()
        self._select(cursor, PositionRecord, Position, "accountID=%s" % accountID)
        positions = {}
        for result in cursor.fetchall():
            position = Position(*result)
            positions[position.code] = position
        return positions

    def _cash(self, accountID):
        cursor = self.connection.cursor()
        self._select(cursor, CashRecord, Cash, "accountID=%s" % accountID)
        result = cursor.fetchone()
        return Cash(*result)

    def _select(self, cursor, record, instance, conditions):
        cursor.execute(
            self.tables[record.__name__].select(
                ",".join(instance.__slots__),
                where=conditions
            )
        )


class MysqlNothingChanged(Exception): pass


def drop_all(engine):
    cursor = engine.connection.cursor()
    for table in engine.tables.values():
        cursor.execute(table.drop)


def create_all(engine):
    cursor = engine.connection.cursor()
    for table in engine.tables.values():
        cursor.execute(table.create)


def today():
    return date.today().strftime("%Y-%m-%d 00:00:00")


from datetime import datetime


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    from fxdayu_ex.utils.logger import dict_initiate
    from fxdayu_ex.module.enums import OrderStatus

    dict_initiate()

    engine = MysqlEngine("jdbc:mysql://localhost:3306/broker?user=root&password=fxdayu")
    print(engine.accounts())
    # engine.start()
    # # engine.buy_order(
    # #     order=Order(111, 112230, "000001.XSHE", 1000, price=100000, frzAmt=100000000, time=now(), cnfmTime=now()),
    # #     cash=Cash(111, 10000000000-100000000, 100000000)
    # # )

    # engine.trade(
    #     cash=Cash(111, 10000000000 - 100000000),
    #     order=Order(111, 112230, "000001.XSHE", 1000, price=100000, cumQty=1000, cumAmt=100000000, frzAmt=100000000, orderStatus=OrderStatus.FILLED, time=now(), cnfmTime=now()),
    #     trade=Trade(111, 112230, 112234, "000001.XSHE", 1000, 100000, orderStatus=OrderStatus.FILLED, time=now()),
    #     position=Position(111, "000001.XSHE", 0, 0, today=1000)
    # )