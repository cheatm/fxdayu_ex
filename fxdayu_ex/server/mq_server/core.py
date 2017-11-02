from fxdayu_ex.server.frame.core import Core


class ExCore(Core):

    def __init__(self, req_queue, resp_queue, exchange, broker, orderIDs, mysql):
        super(ExCore, self).__init__(req_queue, exchange, broker, orderIDs)
        self.response = resp_queue
        self.mysql = mysql

    @classmethod
    def from_mysql(cls):
        return cls()

    def trade_success(self, trade):
        super(ExCore, self).trade_success(trade)


    def order_success(self, order):
        super(ExCore, self).order_success(order)

