# encoding:utf-8
from fxdayu_ex.module.storage import Trade
from fxdayu_ex.module.enums import BSType, OrderType, OrderStatus
from fxdayu_ex.utils.id_generator import TimerIDGenerator
from datetime import datetime


CODE = "code"
VOLUME = "volume"
PRICE = "price"
ASK = "ask"
BID = "bid"
DATE = "date"
TIME = "time"


class Exchange(object):

    def __init__(self, broker, pool):
        self.broker = broker
        self.pool = pool

    def on_tick(self, tick):
        for trade in self.pool.on_tick(tick):
            self.broker.trade(trade)


class OrderPool(object):

    def __init__(self, **packs):
        self.packs = packs

    def put(self, order):
        try:
            pack = self.packs[order.code]
        except KeyError:
            pack = OrderPack(order.code)
            self.packs[order.code] = pack

        pack.put(order)

    def on_tick(self, tick):
        try:
            pack = self.packs[tick[CODE]]
        except KeyError:
            return tuple()

        return pack.on_tick(tick)



class OrderPack(object):

    def __init__(self, code):
        self.code = code
        self.orders = dict()

    def on_tick(self, tick):
        for orderID, order in self.orders.copy().items():
            yield from transactor.buy(order, tick)
            if order.unfilled == 0:
                self.orders.pop(order)


    def put(self, order):
        self.orders[order.orderID] = order


class Transactor(object):

    def __init__(self, ids, buy_rate, sell_rate):
        self.ids = ids
        self.br = buy_rate
        self.sr = sell_rate


    def buy(self, order, tick):
        for price, volume in tick[ASK]:
            if order.price >= price:
                if order.unfilled <= volume:
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, order.unfilled, price,
                        order.qty*price*self.br, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
                else:
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, volume, price,
                        order.volume*price*self.br, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
            else:
                return


def combine(date, time):
    day = date % 100
    month = int((date - day) % 10000 / 100)
    year = int(date/10000)
    ms = time % 1000
    time = time-ms
    second = int((time % 100000)/1000)
    time = time - second
    minute = int(time % 10000000 / 100000)
    hour = int(time / 10000000)
    return datetime(year, month, day, hour, minute, second, ms*1000)



Tick = {'date': 20171017,
        'code': '600565.XSHG',
        'ask': list(zip([5.27, 5.28, 5.29, 5.3, 5.31], [237200, 109700, 161500, 137200, 82400])),
        'time': 95615640,
        'bid': list(zip([5.26, 5.25, 5.24, 5.23, 5.22], [24800, 277300, 290200, 289200, 208000]))}


transactor = Transactor(TimerIDGenerator.year(), 0.00001, 0.00001)

if __name__ == '__main__':
    print(combine(Tick[DATE], Tick[TIME]))