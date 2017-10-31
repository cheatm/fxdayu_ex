from fxdayu_ex.utils.mysql import *
from fxdayu_ex.server.frame.engine import Consumer
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
        self.order_table = OrderTable()
        self.cash_table = CashTable()
        self.trade_table = TradeTable()
        self.position_table = PositionTable()

    def buy_order(self, order, cash):
        self.queue.put(
            (self.cash_table.update(cash),
             self.order_table.insert(order))
        )

    def sell_order(self, order, position):
        self.queue.put(
            (self.position_table.update(position),
             self.order_table.insert(order))
        )

    def trade(self, cash, order, trade, position):
        self.queue.put((self.cash_table.update(cash),
                        self.order_table.update(order),
                        self.trade_table.insert(trade),
                        self.position_table.update(position)))

    def buy_cancel(self, order, cash):
        self.queue.put((self.cash_table.update(cash),
                        self.order_table.update(order)))

    def sell_cancel(self, order, position):
        self.queue.put(self.position_table.update(position),
                       self.order_table.update(order))

    def handle(self, quest):
        cursor = self.connection.cursor()
        for query in quest:
            cursor.execute(query)
        self.connection.commit()


