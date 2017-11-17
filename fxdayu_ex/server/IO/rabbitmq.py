from fxdayu_ex.server.IO.structures import REQUEST, RESPONSE, TICK, ALL, \
    get_req_ex, get_tick_ex, get_resp_ex, client_req_queue, all_tick_queue
from fxdayu_ex.utils.rbmq.con import get_con, consumer_ack, consumer_no_ack
from fxdayu_ex.utils.rbmq.objects import RabbitStructure
from fxdayu_ex.server.frame.engine import TickEvent, ReqEvent
from fxdayu_ex.module.request import CLASSES
from queue import Queue
import logging
import json
from fxdayu_ex.server.frame.engine import Consumer


class ClientRespPublisher(Consumer):

    def __init__(self, rb_exchange, resp_queue):
        self.rb_exchange = rb_exchange
        super(ClientRespPublisher, self).__init__(resp_queue, 5)

    def handle(self, quest):
        try:
            resp = json.dumps(quest.to_dict())
        except:
            pass
        else:
            self.response(resp, quest.accountID)

    def response(self, body, accountID):
        self.rb_exchange.publish("", body, routing_key=accountID)


class MQReceiver(object):
    def __init__(self, queue):
        self.queue = queue

    def on_tick(self, tick):
        try:
            tick = json.loads(tick)
        except Exception as e:
            logging.warning("Load tick %s fail: %s", tick, e)
        else:
            self.queue.put(TickEvent(tick))

    def on_req(self, req):
        logging.debug(req)
        try:
            req = json.loads(req)
            obj = CLASSES[req["cls"]].from_dict(req)
        except Exception as e:
            logging.warning("Load req %s fail: %s", req, e)
        else:
            self.queue.put(ReqEvent(obj))


from threading import Thread


class RabbitConnection(Thread):

    def __init__(self, url, req_queue, resp_queue):
        super(RabbitConnection, self).__init__(name="RabbitConnection")
        self.url = url
        self.connection = get_con(url)
        self.receiver = MQReceiver(req_queue)
        self.exchanges = self.init_ex()
        self.queues = self.init_queue()
        self.publisher = ClientRespPublisher(self.exchanges[RESPONSE], resp_queue)
        self.structure = RabbitStructure(
            self.connection,
            self.exchanges,
            self.queues
        )

    def connect(self):
        logging.debug("Start ClientRespPublisher.")
        self.publisher.start()
        logging.debug("Start Tornado ioloop.")
        self.connection.ioloop.start()

    def init_queue(self):
        return {
            ALL: all_tick_queue(self.receiver.on_tick),
            REQUEST: client_req_queue(self.receiver.on_req)
        }

    def init_ex(self):
        return {
            TICK: get_tick_ex(),
            REQUEST: get_req_ex(),
            RESPONSE: get_resp_ex()
        }

    def start(self):
        self.publisher.start()
        self.connection.ioloop.start()