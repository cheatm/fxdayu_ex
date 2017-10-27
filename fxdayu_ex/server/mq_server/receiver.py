from fxdayu_ex.utils.rbmq import MQHeaderListener, MQRequestListener
from fxdayu_ex.server.frame.engine import TickEvent, ReqEvent
from fxdayu_ex.server.mq_server.transmission import load_req, load_cancel
import json


class TickListener(MQHeaderListener):

    def __init__(self, queue, connection, exchange):
        super(TickListener, self).__init__(connection, exchange)
        self.queue = queue
        self.add("all", {})

    def handle(self, tick):
        try:
            tick = json.loads(tick)
        except Exception as e:
            self.tick_load_exception(tick, e)
        else:
            self.queue.put(TickEvent(tick))

    def tick_load_exception(self, tick, e):
        pass


class ClientRequestListener(MQRequestListener):

    def __init__(self, queue, connection, exchange):
        self.queue = queue
        super(ClientRequestListener, self).__init__(connection, exchange)
        self.add("ReqOrder", self.handle_req_order)
        self.add("CancelOrder", self.handle_cancel_order)

    def handle_req_order(self, req):
        try:
            req = load_req(json.loads(req))
        except Exception as e:
            self._load_req_fail(req, e)
        else:
            self.queue.put(ReqEvent(req))

    def _load_req_fail(self, req, e):
        pass

    def handle_cancel_order(self, cancel):
        try:
            cancel = load_cancel(json.loads(cancel))
        except Exception as e:
            self._load_req_fail(cancel , e)
        else:
            self.queue.put(ReqEvent(cancel))
