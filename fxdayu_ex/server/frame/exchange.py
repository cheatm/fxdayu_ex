# encoding:utf-8
from fxdayu_ex.module.instance import Trade, Order
from fxdayu_ex.module.enums import BSType, OrderType, OrderStatus
from datetime import datetime
from queue import deque


CODE = "code"
VOLUME = "volume"
PRICE = "price"
ASK = "ask"
BID = "bid"
DATE = "date"
TIME = "time"
PRE = "pre"


class Exchange(object):

    def __init__(self, pool, transactor):
        self.pool = pool
        self.transactor = transactor
        self.snapshots = {}
        self.limits = {BSType.BUY.value: 1.1, BSType.SELL.value:0.9}

    def price_limit(self, code, bstype):
        snapshot = self.snapshots[code]
        return int((snapshot[PRE] * self.limits[bstype.value])/100)*100

    def on_tick(self, tick):
        code = tick[CODE]
        self.snapshots[code] = tick
        pack = self.pool.pack(code)
        for order in pack:
            yield from self.transactor[order.bsType](order, tick)
            pack.wait(order)
        pack.recycle()


class OrderPool(object):

    def __init__(self, **packs):
        self.packs = packs

    @classmethod
    def from_dict(cls, dct):
        return cls(**dict(cls.iter_dict(dct)))

    @staticmethod
    def iter_dict(dct):
        for code, orders in dct:
            pack = OrderPack(code)
            for order in orders:
                pack.put(order)
            yield code, pack

    def put(self, order):
        self.pack(order.code).put(order)

    def cancel(self, order):
        self.pack(order.code).cancel(order)

    def pack(self, name):
        try:
            pack = self.packs[name]
        except KeyError:
            pack = OrderPack(name)
            self.packs[name] = pack

        return pack


class OrderPack(object):

    def __init__(self, code):
        self.code = code
        self._orders = deque()
        self._wait = deque()

    def __iter__(self):
        while self._orders.__len__():
            yield self._orders.popleft()

    def recycle(self):
        while self._wait.__len__():
            order = self._wait.pop()
            self._orders.appendleft(order)

    def wait(self, order):
        if order.unfilled > 0:
            self._wait.append(order)

    def put(self, order):
        self._orders.append(order)

    def cancel(self, order):
        try:
            self._orders.remove(order)
        except:
            try:
                self._wait.remove(order)
            except Exception:
                pass


class Transactor(object):

    def __init__(self, ids, buy_rate, sell_rate):
        self.ids = ids
        self.br = buy_rate
        self.sr = sell_rate
        self.funcs = {BSType.BUY.value: self.buy,
                      BSType.SELL.value: self.sell}

    def __getitem__(self, item):
        return self.funcs[item.value]

    def buy(self, order, tick):
        for price, volume in tick[ASK]:
            if order.price >= price and (order.unfilled > 0):
                if order.unfilled <= volume:
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, order.unfilled, price,
                        order.orderType, order.bsType,
                        order.unfilled*price*self.br, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
                else:
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, volume, price,
                        order.orderType, order.bsType,
                        volume*price*self.br, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
            else:
                return

    def sell(self, order, tick):
        for price, volume in tick[BID]:
            if order.price <= price and (order.unfilled > 0):
                if order.unfilled <= volume:
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, order.unfilled, price,
                        order.orderType, order.bsType,
                        order.unfilled*price*self.br, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
                else:
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, volume, price,
                        order.orderType, order.bsType,
                        volume*price*self.br, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
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



Tick = {'date': 20171018,
        'code': '300667.XSHE',
        'ask': [[46.4, 2600], [46.41, 600], [46.42, 1300], [46.43, 2900], [46.44, 200]],
        'time': 94109000,
        'bid': [[46.39, 200], [46.29, 1000], [46.28, 400], [46.2, 300], [46.19, 600]]}


def transact(order, trade):
    order.cum_qty += trade.qty


def t():

    od = Order(orderID=0, code='300667.XSHE', qty=4000, price=46.42,
               orderType=OrderType.LIMIT, bsType=BSType.BUY)
    # od = Order(orderID=0, code='300667.XSHE', qty=4000, price=46.39,
    #            order_type=OrderType.LIMIT, bs_type=BSType.SELL)
    op = OrderPack('300667.XSHE')
    op.put(od)
    for order in op:
        op.wait(order)
    op.recycle()


if __name__ == '__main__':
    t()