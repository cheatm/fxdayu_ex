# encoding:utf-8
from fxdayu_ex.server.exchange.engine import TickListener
from pika import TornadoConnection, URLParameters
import json


TICK_EXCHANGE = "Tick"


class MQTickListener(TickListener):

    def __init__(self, connection, listen=TICK_EXCHANGE):
        self.channel = None
        self.queue = ""
        self.listen = listen
        if isinstance(connection, TornadoConnection):
            self.connection = connection
            connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        channel.queue_declare(self.on_open_queue, auto_delete=True)

    def on_open_queue(self, method):
        self.queue = method.method.queue
        self.channel.queue_bind(self.on_queue_bind, self.queue, self.listen)

    def on_queue_bind(self, method):
        self.channel.basic_consume(self.consumer_callback, self.queue, no_ack=True)

    def consumer_callback(self, channel, deliver, properties, body):
        try:
            print(json.loads(body))
        except Exception as e:
            print(e)


def get_open_con():
    from threading import Thread
    connection = TornadoConnection(URLParameters("amqp://192.168.0.104:10009"))
    Thread(target=connection.ioloop.start).start()
    while not connection.is_open:
        pass
    return connection


if __name__ == '__main__':
    MQTickListener(get_open_con())