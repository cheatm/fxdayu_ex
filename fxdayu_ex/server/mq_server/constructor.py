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
                 rule = "year",
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

        exchange = self.init_exchange(rule, buy_rate, sell_rate)
        broker = self.init_broker()

        self.core = ExCore(self.req_queue,
                           self.resp_queue,
                           exchange,
                           broker, )

    def init_order_pool(self):


    def init_broker(self):
        try:
            return Broker(self.mysql_engine.accounts())
        except Exception as e:
            logging.error("Initiate core:broker fail: %s", e)
            self.end_with_exception()

    def init_exchange(self, rule, buy_rate, sell_rate):
        try:
            return Exchange.quick(rule, buy_rate, sell_rate)
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