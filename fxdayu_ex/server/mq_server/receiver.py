from fxdayu_ex.server.frame.engine import TickEvent, ReqEvent
from fxdayu_ex.module.request import CLASSES
import logging
import json


class TickListener(object):
    def __init__(self, queue):
        self.queue = queue

    def on_tick(self, tick):
        try:
            tick = json.loads(tick)
        except Exception as e:
            logging.warning("Load tick error: %s", tick)
        else:
            self.queue.put(TickEvent(tick))


class ClientRequestListener(object):

    def __init__(self, queue):
        self.queue = queue

    def on_req(self, req):
        try:
            req = json.loads(req)
            obj = CLASSES[req["type"]].from_dict(req['data'])
        except Exception as e:
            logging.warning("Load req error: %s", req)
        else:
            self.queue.put(ReqEvent(obj))