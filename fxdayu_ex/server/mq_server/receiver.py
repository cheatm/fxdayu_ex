from fxdayu_ex.server.frame.engine import TickEvent, ReqEvent
from fxdayu_ex.module.request import CLASSES
import logging
import json


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
        try:
            req = json.loads(req)
            obj = CLASSES[req["cls"]].from_dict(req)
        except Exception as e:
            logging.warning("Load req %s fail: %s", req, e)
        else:
            self.queue.put(ReqEvent(obj))