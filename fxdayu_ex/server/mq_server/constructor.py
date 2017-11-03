# encoding:utf-8
import logging
from fxdayu_ex.server.IO.mysql_engine import MysqlEngine
from fxdayu_ex.server.IO.rabbitmq import RabbitConnection
from fxdayu_ex.utils.id_generator import get_timer_id
from fxdayu_ex.server.mq_server.core import ExCore
from fxdayu_ex.server.frame.exchange import Exchange, OrderPool, Transactor
from fxdayu_ex.server.frame.broker import Broker, Account
from fxdayu_ex.utils.logger import dict_initiate, file_initiate
from queue import  Queue

dict_initiate()


class Constructor(object):

    def __init__(self,
                 ampq_url,
                 mysql_url,
                 logfile=None,
                 logconfig=None,
                 orderID_rule="year",
                 tradeID_rule="year",
                 buy_rate="5/10000",
                 sell_rate="5/10000"):
        if logconfig:
            file_initiate(logconfig)
        else:
            dict_initiate(logfile)

        logging.debug("Initiating Exchange server.")

        self.resp_queue = Queue()
        self.req_queue = Queue()

        self.mysql_engine = self.init_sql(mysql_url)

        self.tradeIDs = self.init_IDs(tradeID_rule)
        self.orderIDs = self.init_IDs(orderID_rule)
        self.broker = self.init_broker()
        self.pool = self.init_order_pool()
        self.transactor = self.init_transactor(buy_rate, sell_rate)
        self.exchange = self.init_exchange()

        self.core = ExCore(self.req_queue,
                           self.resp_queue,
                           self.exchange,
                           self.broker,
                           self.orderIDs,
                           self.mysql_engine)

    def init_IDs(self, rule):
        return get_timer_id(rule)

    def init_order_pool(self):
        orders = {}
        for account in self.broker.accounts.values():
            for order in account.orders.values():
                orders.setdefault(order.code, []).append(order)

        return OrderPool.from_dict(orders)

    def init_broker(self):
        try:
            return Broker(self.mysql_engine.accounts())
        except Exception as e:
            logging.error("Initiate core:broker fail: %s", e)
            self.end_with_exception()

    def init_transactor(self, buy_rate, sell_rate):
        pass

    def init_exchange(self):
        try:
            return Exchange(self.pool, self.transactor)
        except Exception as e:
            logging.error("Initiate core:exchange fail: %s", e)
            self.end_with_exception()

    def init_sql(self, url):
        try:
            return MysqlEngine(url)
        except Exception as e:
            logging.error("Initiate MysqlEngine fail: %s", e)
            self.end_with_exception()


    def end_with_exception(self):
        import sys
        logging.error('Service exit for unexpected exception.')
        sys.exit(-1)





if __name__ == '__main__':
    Constructor("amqp://xinge:fxdayu@localhost:5672")