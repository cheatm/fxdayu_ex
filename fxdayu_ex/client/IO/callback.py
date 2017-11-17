import logging
from queue import Queue
import json
from fxdayu_ex.module.instance import Order, Trade, SnapShot
from fxdayu_ex.server.frame.engine import Consumer


class ClientCallback(Consumer):

    def __init__(self, accountID):
        super(ClientCallback, self).__init__(Queue(), 3, name="RespConsumer")
        self.accountID = accountID

        self.instances = {
            Order.__name__: (Order, self.on_order),
            Trade.__name__: (Trade, self.on_trade),
            SnapShot.__name__: (SnapShot, self.on_snapshot)
        }

    def on_order(self, order):
        pass

    def on_trade(self, trade):
        pass

    def on_snapshot(self, snapshot):
        pass

    def on_resp(self, resp):
        logging.info(resp)
        self.queue.put(resp)

    def handle(self, quest):
        try:
            response = json.loads(quest)
            cls, handler = self.instances[response.pop("cls")]
            obj = cls(**response)
        except Exception as e:
            logging.warning("Load resp: %s fail: %s", quest, str(e))
            return

        try:
            handler(obj)
        except Exception as e:
            logging.error("Handle %s fail: %s", obj, e)