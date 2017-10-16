# encoding:utf-8
from queue import deque


CODE = "code"
VOLUME = "volume"
PRICE = "price"
ASK = "ask"
BID = "bid"
DATE = "date"
TIME = "time"


class TickListener(object):

    # def __init__(self, exchange=None):
    #     self.exchange = exchange

    def handle(self, tick):
        pass



class OrderPack(object):

    def __init__(self, code):
        self.code = code
        self._wait_list = deque()
        self._back_list = deque()

    def handle(self, tick):
        pass