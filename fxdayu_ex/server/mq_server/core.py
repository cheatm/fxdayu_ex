from fxdayu_ex.server.frame.core import Core


class ExCore(Core):

    def __init__(self, req_queue, resp_queue, exchange, broker, orderIDs, mysql):
        super(ExCore, self).__init__(req_queue, exchange, broker, orderIDs)
        self.response = resp_queue
        self.mysql = mysql

    @classmethod
    def from_mysql(cls):
        return cls()

    def buy_order_success(self, order, cash):
        self.mysql.buy_order(order, cash)
        self.response.put(order)

    def sell_order_success(self, order, position):
        self.mysql.sell_order(order, position)
        self.response.put(order)
