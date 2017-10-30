# encoding:utf-8
from fxdayu_ex.server.frame.engine import Consumer
from fxdayu_ex.server.mq_server.structures import get_req_ex, client_resp_queue
from fxdayu_ex.utils.rbmq.objects import RabbitStructure
from fxdayu_ex.utils.rbmq.con import consumer_ack, get_con
from fxdayu_ex.utils.logger import dict_initiate
import logging
from queue import Queue


REQUESTS = "ClientRequest"
RESPONSE = "ClientResponse"


class MQClientInstance(Consumer):

    def __init__(self, accountID, connection):
        super(MQClientInstance, self).__init__(Queue(), 5)
        self.accountID = accountID
        self.connection = connection
        self.exchange = get_req_ex()
        self.rqueue = client_resp_queue(self.accountID, consumer_ack(self.on_resp))
        self.structure = RabbitStructure(
            self.connection,
            {REQUESTS: self.exchange},
            {self.accountID: self.rqueue}
        )

    def on_resp(self, resp):
        logging.debug(resp)


if __name__ == '__main__':
    dict_initiate()
    con = get_con("amqp://xinge:fxdayu@localhost:5672")
    MQClientInstance(134, con)
    con.ioloop.start()
