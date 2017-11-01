from fxdayu_ex.server.frame.core import Core


class ExCore(Core):

    def __init__(self, exchange, broker, orderIDs, tradeIDs, response, mysql):
        super(ExCore, self).__init__(exchange, broker, orderIDs, tradeIDs)
        self.response = response
        self.mysql = mysql

    @classmethod
    def from_mysql(cls):
        return cls()

    def trade_success(self, trade):
        super(ExCore, self).trade_success(trade)


    def order_success(self, order):
        super(ExCore, self).order_success(order)

