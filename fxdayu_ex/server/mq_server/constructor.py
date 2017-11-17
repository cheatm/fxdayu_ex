# encoding:utf-8
import logging
from fxdayu_ex.server.IO.mysql_engine import MysqlEngine
from fxdayu_ex.server.IO.rabbitmq import RabbitConnection
from fxdayu_ex.utils.id_generator import get_timer_id
from fxdayu_ex.server.mq_server.core import ExCore
from fxdayu_ex.server.frame.exchange import Exchange, OrderPool, Transactor
from fxdayu_ex.server.frame.broker import Broker
from fxdayu_ex.utils.logger import dict_initiate, file_initiate
from queue import  Queue
from threading import Thread

dict_initiate()


class Constructor(object):

    def __init__(self,
                 amqp_url,
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

        # Core Event Queue
        self.resp_queue = Queue()
        self.req_queue = Queue()

        # Exchange Core
        logging.debug("Initiating ExchangeCore.")

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

        logging.debug('Successfully initiated ExchangeCore.')

        # MQ Connection
        self.mq = self.init_mq(amqp_url)
        logging.debug("Successfully initiated MQ structure")

        self._running = False

    def run(self):
        while self._running:
            self.routing()

    def routing(self):


    def init_mq(self, url):
        logging.debug('Initiating MQ connection.')

        try:
            return RabbitConnection(url, self.req_queue, self.resp_queue)
        except Exception as e:
            logging.error("Initiate MQ connection: %s fail: %s.", url, e)
            self.end_with_exception()


    def init_IDs(self, rule):
        logging.debug("Initiating IDGenerator with rule: %s.", rule)
        try:
            return get_timer_id(rule)
        except Exception as e:
            logging.error("Initiate core: IDGenerator with rule: %s fail: %s.", rule, e)
            logging.warning("Initiate IDGenerator with default rule: year.")
            return get_timer_id("year")

    def init_order_pool(self):
        logging.debug("Initiating OrderPool.")
        orders = {}
        for account in self.broker.accounts.values():
            for order in account.orders.values():
                orders.setdefault(order.code, []).append(order)

        return OrderPool.from_dict(orders)

    def init_broker(self):
        logging.debug("Initiating Broker and Accounts.")
        try:
            accounts = self.mysql_engine.accounts()
            logging.debug("Restored %d accounts from database", len(accounts))
            return Broker(accounts)
        except Exception as e:
            logging.error("Initiate core:broker fail: %s.", e)
            self.end_with_exception()

    def init_transactor(self, buy_rate, sell_rate):
        from fxdayu_ex.utils.cal import Rate

        logging.debug("Initiating transactor.")
        try:
            br = Rate.from_str(buy_rate)
            sr = Rate.from_str(sell_rate)
        except Exception as e:
            logging.warning("Initiate transact fee rate fail with buy_rate=%s, sell_rate=%s.", buy_rate, sell_rate)
            logging.warning("Use default rate(5/10000).")
            br = Rate(5, 10000)
            sr = Rate(5, 10000)

        return Transactor(self.tradeIDs, br, sr)

    def init_exchange(self):
        try:
            return Exchange(self.pool, self.transactor)
        except Exception as e:
            logging.error("Initiate core:exchange fail: %s.", e)
            self.end_with_exception()

    def init_sql(self, url):
        logging.debug("Initiating Mysql Engine with url: %s.", url)
        try:
            return MysqlEngine(url)
        except Exception as e:
            logging.error("Initiate MysqlEngine fail: %s.", e)
            self.end_with_exception()

    def end_with_exception(self):
        import sys
        logging.error('Service exit for unexpected exception.')
        sys.exit(-1)

    def start(self):
        logging.debug("Start MysqlEngine.")
        self.mysql_engine.start()
        logging.debug("Start ExchangeCore.")
        self.core.start()
        logging.debug("Start MQ connection.")
        self.mq.connect()


if __name__ == '__main__':
    Constructor("amqp://xinge:fxdayu@localhost:5672",
                "jdbc:mysql://localhost:3306/broker?user=root&password=fxdayu").start()