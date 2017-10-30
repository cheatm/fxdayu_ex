from fxdayu_ex.server.frame.core import Core


class ExCore(Core):

    def __init__(self, exchange, broker, orderIDs, tradeIDs, resp_queue):
        super(ExCore, self).__init__(exchange, broker, orderIDs, tradeIDs)
        self.resp_queue = resp_queue

    @classmethod
    def from_mysql(cls):
        return cls()

    @classmethod
    def from_test(cls, resp):
        from fxdayu_ex.utils.id_generator import TimerIDGenerator
        from fxdayu_ex.utils.cal import Rate
        from fxdayu_ex.server.frame.exchange import Exchange, OrderPool, Transactor
        from fxdayu_ex.server.frame.broker import Broker,Account
        from fxdayu_ex.module.storage import Cash, Position

        orderIDs = TimerIDGenerator.year()
        tradeIDs = TimerIDGenerator.year()

        exchange = Exchange(OrderPool(), transactor=Transactor(tradeIDs, Rate(5, 10000), Rate(5, 10000)))
        accID = 134
        broker = Broker(
            {accID: Account(accID,
                            Cash(accID, 10000000000),
                            {"000001.XSHE": Position(accID, "000001.XSHE", 1000, available=1000)},
                            {})})

        return cls(
            exchange,
            broker,
            orderIDs,
            tradeIDs,
            resp
        )

    def trade_success(self, trade):
        super(ExCore, self).trade_success(trade)
        self.resp_queue.put(trade)

    def order_success(self, order):
        super(ExCore, self).order_success(order)
        self.resp_queue.put(order)
