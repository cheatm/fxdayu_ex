# encoding:utf-8
from pika import TornadoConnection
from fxdayu_ex.utils.rbmq.con import get_con, consumer_ack, consumer_no_ack
from fxdayu_ex.utils.rbmq.objects import RabbitStructure
from fxdayu_ex.server.mq_server.receiver import MQReceiver
from fxdayu_ex.server.mq_server.publisher import ClientRespPublisher
from fxdayu_ex.server.mq_server.structures import REQUEST, RESPONSE, TICK, ALL, \
    get_req_ex, get_tick_ex, get_resp_ex, client_req_queue, all_tick_queue
from fxdayu_ex.server.mq_server.core import ExCore
from fxdayu_ex.utils.logger import dict_initiate
import logging


dict_initiate()


class Constructor(object):

    def __init__(self, url):
        logging.debug("start")
        self.connection = get_con(url)
        self.mqex = self.init_ex()
        self.resp = ClientRespPublisher(self.mqex[RESPONSE])
        self.core = ExCore.from_test(self.resp.queue)
        self.receiver = MQReceiver(self.core.queue)

        self.mqq = self.init_queue()

        self.mq = RabbitStructure(
            self.connection,
            self.mqex,
            self.mqq
        )

    def init_queue(self):
        return {
            ALL: all_tick_queue(consumer_no_ack(self.receiver.on_tick)),
            REQUEST: client_req_queue(consumer_ack(self.receiver.on_req))
        }

    def init_ex(self):
        return {
            TICK: get_tick_ex(),
            REQUEST: get_req_ex(),
            RESPONSE: get_resp_ex()
        }

    def start(self):
        self.core.start()
        self.resp.start()
        self.connection.ioloop.start()


if __name__ == '__main__':
    Constructor("amqp://xinge:fxdayu@localhost:5672").start()