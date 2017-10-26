from fxdayu_ex.server.frame.framework import FrameWork, TickEvent, ReqEvent, RespEvent
from fxdayu_ex.module.request import ReqOrder, CancelOrder
from fxdayu_ex.utils.rbmq import MQHeaderListener
from fxdayu_ex.module.enums import OrderType, BSType
from fxdayu_ex.server.mq_server.transmission import load_req
import json


class MQFrameWork(FrameWork):

    def __init__(self, connection, exchange, broker, orderIDs, tradeIDs):
        self.connection = connection
        self.listener = MQHeaderListener(self.connection, "Tick")
        self.listener.handle = self.put_tick
        self.listener.add("all", {})
        super(MQFrameWork, self).__init__(exchange, broker, orderIDs, tradeIDs)

    def start(self):
        super(MQFrameWork, self).start()
        self.connection.ioloop.start()

    def listen(self, code):
        receiver = self.listener.receivers.get(code, None)
        print("listen", code)
        if receiver is None:
            self.listener.add(code, {'code': code})
        else:
            if not receiver.listening:
                receiver.listen(self.listener.channel, self.put_tick)

    def put_tick(self, tick):
        try:
            tick = json.loads(tick)
        except Exception as e:
            pass
        self.put(TickEvent(tick))

    def put_req_order(self, req):
        try:
            req = load_req(json.loads(req))
        except Exception as e:
            self._load_req_fail(req, e)
        else:
            self.put(ReqEvent(req))

    def _load_req_fail(self, req, e):
        print(req, e)

def simulation():
    accountID = 103
    frame = generate(accountID)
    from fxdayu_ex.module.enums import BSType, OrderType

    req = ReqOrder(accountID, "000001.XSHE", 1000, price=111000, orderType=OrderType.LIMIT, bsType=BSType.BUY)
    frame.put(ReqEvent(req))
    frame.start()


def generate(accountID):
    from fxdayu_ex.utils.rbmq import get_con, remote
    from fxdayu_ex.module.storage import Cash, Position
    from fxdayu_ex.server.frame.exchange import Exchange, OrderPool, Transactor
    from fxdayu_ex.server.frame.broker import Broker, Account
    from fxdayu_ex.utils.id_generator import TimerIDGenerator
    from fxdayu_ex.utils.cal import Rate

    tradeIDs = TimerIDGenerator.year()
    orderIDs = TimerIDGenerator.year()
    pool = OrderPool()
    transactor = Transactor(tradeIDs, Rate(5, 10000), Rate(5, 10000))

    account = Account(accountID, Cash(accountID, 100000000000), {}, {})
    broker = Broker({accountID: account})
    frame = MQFrameWork(get_con(remote), Exchange(pool, transactor), broker, orderIDs, tradeIDs)
    return frame


if __name__ == '__main__':
    simulation()
