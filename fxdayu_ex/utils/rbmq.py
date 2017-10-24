# encoding:utf-8
from pika import TornadoConnection, URLParameters
import json


class MQHeaderListener(object):

    def __init__(self, connection, exchange):
        """

        :param connection: pika.TornadoConnection object
        :param exchange: str, which header exchange to listen
        """
        self.channel = None
        self.connection = connection
        self.connection.add_on_open_callback(self.on_connection_open)
        self.exchange = exchange
        self.receivers = {}

    def add(self, name, headers):
        receiver = HeaderReceiver(name, self.exchange, headers, self.handle, self.channel)
        if self.channel is not None and self.channel.is_open:
            receiver.listen(self.channel)
        self.receivers[name] = receiver

    def stop(self, name):
        receiver = self.receivers[name]
        receiver.cancel()

    def connect(self):
        if not self.connection.is_open:
            self.connection.ioloop.start()
        else:
            self.on_connection_open(self.connection)

    def on_connection_open(self, connection):
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        for name, receiver in self.receivers.items():
            receiver.listen(self.channel)

    def load_exception(self, e):
        pass

    def handle(self, tick):
        try:
            tick = json.loads(tick)
        except Exception as e:
            self.load_exception(e)
            return

        self.on_tick(tick)

    def on_tick(self, tick):
        print(tick)

    @classmethod
    def url_start(cls, url, exchange, *codes):
        """

        :param url: str, rabbitmq url to connect
        :param exchange: str, header exchange to listen
        :param codes: which stock's tick message to listen
        :return:
        """
        con = get_con(url)
        listener = cls(con, exchange)
        for code in codes:
            listener.add(code, {'code': code})
        listener.connect()


class HeaderReceiver(object):

    def __init__(self, tag, exchange, header):
        self.tag = tag
        self.exchange = exchange
        self.header = header
        self.handler = None
        self.channel = None
        self.queue = None

    def listen(self, channel, handler):
        self.channel = channel
        self.handler = handler
        self.channel.queue_declare(self.on_open_queue, auto_delete=True)

    def cancel(self):
        self.channel.basic_cancel(self.on_cancel_consumer, consumer_tag=self.tag)

    def on_cancel_consumer(self, method):
        self.__delattr__("handler")

    def on_open_queue(self, method):
        self.queue = method.method.queue
        self.channel.queue_bind(self.on_queue_bind, self.queue, self.exchange, "", arguments=self.header)

    def on_queue_bind(self, method):
        self.channel.basic_consume(self.consumer_callback, self.queue, consumer_tag=self.tag, no_ack=True)

    def consumer_callback(self, channel, deliver, properties, body):
        self.handler(body)


def get_con(url):
    return TornadoConnection(URLParameters(url))


def get_open_con(url):
    from threading import Thread
    connection = get_con(url)

    Thread(target=connection.ioloop.start).start()
    while not connection.is_open:
        pass
    return connection



if __name__ == '__main__':

    MQHeaderListener.url_start("amqp://xinge:fxdayu@localhost:5672", "Tick",
                               "000001.XSHE", "000002.XSHE", "600000.XSHG")


