# encoding:utf-8
from pika import TornadoConnection, URLParameters, BasicProperties
import json


CONNECTION_CLOSE = "ConnectionClose"


class MQExchangeConstructor(object):

    def __init__(self, connection, exchange):
        """

        :param connection: pika.TornadoConnection object
        :param exchange: str, which exchange to listen
        """
        self.exchange = exchange
        self.connection = connection
        self.connection.add_on_open_callback(self.on_connection_open)
        self.connection.add_on_close_callback(self.on_connection_close)

    def on_connection_open(self, connection):
        pass

    def on_connection_close(self, connection, reply_code, reply_text):
        pass

    def connect(self):
        if not self.connection.is_open:
            self.connection.ioloop.start()
        else:
            self.on_connection_open(self.connection)


class MQHeaderListener(MQExchangeConstructor):

    def __init__(self, connection, exchange):
        """

        :param connection: pika.TornadoConnection object
        :param exchange: str, which header exchange to listen
        """
        super(MQHeaderListener, self).__init__(connection, exchange)
        self.channel = None
        self.receivers = {}

    def add(self, name, headers):
        receiver = HeaderReceiver(name, self.exchange, headers)
        if self.channel is not None and self.channel.is_open:
            receiver.listen(self.channel, self.handle)
        self.receivers[name] = receiver

    def revoke(self, receiver):
        if not receiver.listening:
            receiver.listen(self.channel, self.handle)

    def stop(self, name):
        receiver = self.receivers[name]
        receiver.cancel()

    def on_connection_open(self, connection):
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        for name, receiver in self.receivers.items():
            receiver.listen(self.channel, self.handle)

    def load_exception(self, e):
        pass

    def handle(self, tick):
        pass

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
        self.listening = False

    def listen(self, channel, handler):
        self.channel = channel
        self.handler = handler
        self.channel.queue_declare(self.on_open_queue, auto_delete=True)

    def cancel(self):
        self.channel.basic_cancel(self.on_cancel_consumer, consumer_tag=self.tag)

    def on_cancel_consumer(self, method):
        self.__delattr__("handler")
        self.channel.queue_delete(None, self.queue)
        self.listening = False

    def on_open_queue(self, method):
        self.queue = method.method.queue
        self.channel.queue_bind(self.on_queue_bind, self.queue, self.exchange, "", arguments=self.header)

    def on_queue_bind(self, method):
        self.channel.basic_consume(self.consumer_callback, self.queue, consumer_tag=self.tag, no_ack=True)
        self.listening = True

    def consumer_callback(self, channel, deliver, properties, body):
        self.handler(body)


class MQRequestListener(MQExchangeConstructor):

    def __init__(self, connection, exchange):
        super(MQRequestListener, self).__init__(connection, exchange)
        self.channel = None
        self._handlers = {}

    def add(self, name, handler):
        self._handlers[name] = consumer_ack(handler)
        if self.channel is not None and self.channel.is_open:
            self._consume(name)

    def _consume(self, name):
        self.channel.queue_declare(self.on_queue_open, name)

    def on_connection_open(self, connection):
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        self.channel.exchange_declare(self.on_exchange_declare, self.exchange)
        self.channel.add_on_close_callback(self.on_channel_close)

    def on_exchange_declare(self, method):
        for name in self._handlers.keys():
            self._consume(name)

    def on_queue_open(self, method):
        queue = method.method.queue
        handler = self._handlers[queue]
        self.channel.basic_consume(handler, queue, consumer_tag=queue)
        self.channel.queue_bind(self.on_queue_bind, method.method.queue, self.exchange, method.method.queue)

    def on_queue_bind(self, method):
        pass

    def on_channel_close(self, *args):
        print(*args)

    def consumer_canceled(self, *args):
        print(*args)


class MQHeaderPublisher(MQExchangeConstructor):

    def __init__(self, connection, exchange):
        self.channel = None
        super(MQHeaderPublisher, self).__init__(connection, exchange)

    def publish(self, body, headers):
        if self.channel.is_open:
            self.channel.basic_publish(self.exchange, "", body, BasicProperties(headers=headers))

    def on_connection_open(self, connection):
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel


def consumer_ack(handler):
    def ack_handler(channel, method, properties, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        handler(body)
    return ack_handler


def reconnect(connection, reply_code, reply_text):
    if reply_text == CONNECTION_CLOSE:
        connection.ioloop.stop()
    else:
        connection.connect()


def normal_close(connection):
    connection.close(reply_text=CONNECTION_CLOSE)


def get_con(url):
    con = TornadoConnection(URLParameters(url))
    con.add_on_close_callback(reconnect)
    return con


def get_open_con(url):
    from threading import Thread
    connection = get_con(url)

    Thread(target=connection.ioloop.start).start()
    while not connection.is_open:
        pass

    return connection


def to_json(body):
    print(json.loads(body))


local = "amqp://xinge:fxdayu@localhost:5672"
remote = "amqp://192.168.0.104:10009"

if __name__ == '__main__':
    mqrl = MQRequestListener(get_con(local), exchange='ClientRequest')
    # mqrl.add("ReqOrder", to_json)
    mqrl.connect()
