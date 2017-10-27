from fxdayu_ex.server.frame.framework import FrameWork, TickEvent, ReqEvent, RespEvent
from fxdayu_ex.module.request import ReqOrder, CancelOrder
from fxdayu_ex.utils.rbmq import MQHeaderListener
from fxdayu_ex.module.enums import OrderType, BSType
from fxdayu_ex.server.mq_server.transmission import load_req
from fxdayu_ex.server.mq_server.publisher import ClientResponse, ClientHeaderPublisher
from fxdayu_ex.server.mq_server.receiver import ClientRequestListener, TickListener
from pika import TornadoConnection


class MQFrame(object):

    def __init__(self, framework, connection):
        self.framework = framework
        self.connection = connection
        self.ticks = TickListener(self.framework.queue, connection, "Tick")
        self.ticks.add("all", {})
        self.request = ClientRequestListener(self.framework.queue, self.connection, "ClientRequest")
        self.response = ClientResponse(publisher=ClientHeaderPublisher(self.connection, exchange="ClientResponse"))
        self.framework.set_response(self.response.queue)
        self.connection.add_on_open_callback(self.on_connection_open)

    def start(self):
        self.framework.start()
        self.connection.ioloop.start()

    def on_connection_open(self, connection):
        pass


class RealTimeFramework(FrameWork):

    def __init__(self, exchange, broker, orderIDs, tradeIDs):
        super(RealTimeFramework, self).__init__(exchange, broker, orderIDs, tradeIDs)
        self.response_queue = None
        self.memory_queue = None
        self.logger = None

    def set_response(self, queue):
        self.response_queue = queue

    def set_memory(self, queue):
        self.memory_queue = queue

    def set_logger(self, logger):
        self.logger = logger


# def simulation():
#     accountID = 103
#     frame = generate(accountID)
#     from fxdayu_ex.module.enums import BSType, OrderType
#
#     req = ReqOrder(accountID, "000001.XSHE", 1000, price=111000, orderType=OrderType.LIMIT, bsType=BSType.BUY)
#     frame.put(ReqEvent(req))
#     frame.start()
#
#

def simulation():
    from fxdayu_ex.utils.rbmq import get_con

    accountID = 103
    framework = generate(accountID)
    mqFrame = MQFrame(framework, connection=get_con("amqp://xinge:fxdayu@localhost:5672"))
    mqFrame.start()


def generate(accountID):
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
    framework = RealTimeFramework(Exchange(pool, transactor), broker, orderIDs, tradeIDs)
    return framework


if __name__ == '__main__':
    from fxdayu_ex.utils.logger import dict_initiate

    dict_initiate("/home/cam/fxdayu_ex")
    simulation()