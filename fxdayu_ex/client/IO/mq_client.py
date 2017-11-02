# encoding:utf-8
import json
import logging
from threading import Thread

from fxdayu_ex.module.instance import Order, Trade, SnapShot
from fxdayu_ex.server.IO.structures import get_resp_ex, get_req_ex, client_resp_queue, REQUEST, RESPONSE
from fxdayu_ex.utils.rbmq.con import get_con
from fxdayu_ex.utils.rbmq.objects import RabbitStructure


class ExRabbitClient(Thread):

    def __init__(self, url, *accountIDs):
        super(ExRabbitClient, self).__init__(name='ExRabbitClient')
        self.accountIDs = accountIDs
        self.url = url
        self.connection = get_con(url)
        self.publisher = get_req_ex()
        self.resp_handlers = {
            Order.__name__: (Order, self.on_order),
            Trade.__name__: (Trade, self.on_trade),
            SnapShot.__name__: (SnapShot, self.on_snapshot)
        }
        self.structure = RabbitStructure(
            self.connection,
            {REQUEST: self.publisher,
             RESPONSE: get_resp_ex()},
            {accountID: client_resp_queue(accountID, self.on_resp) for accountID in self.accountIDs}
        )

    def run(self):
        self.connection.ioloop.start()

    def on_resp(self, resp):
        try:
            response = json.loads(resp)
            cls, handler = self.resp_handlers[response["cls"]]
            obj = cls.from_dict(response)
        except Exception as e:
            logging.warning("Load resp: %s fail: %s", resp, str(e))
        else:
            try:
                handler(obj)
            except Exception as e:
                logging.warning("During handling %s raised %s", obj, e)

    def request(self, req):
        try:
            req = req.to_json()
        except Exception as e:
            logging.warning("Dump %s fail: %s", req, e)
        else:
            self.publisher.publish("", req)

    def on_order(self, order):
        logging.debug(str(order))

    def on_trade(self, trade):
        pass

    def on_snapshot(self, snapshot):
        pass


if __name__ == '__main__':
    from fxdayu_ex.utils.logger import dict_initiate
    dict_initiate()
    ExRabbitClient("amqp://xinge:fxdayu@localhost:5672", 1345, 3422).start()