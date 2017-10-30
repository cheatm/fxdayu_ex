# encoding:utf-8
from pika import TornadoConnection, URLParameters
import json


CONNECTION_CLOSE = "ConnectionClose"


def consumer_ack(handler):
    def ack_handler(channel, method, properties, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        handler(body)
    return ack_handler


def consumer_no_ack(handler):
    def no_ack_handler(channel, method, properties, body):
        return handler(body)
    return no_ack_handler


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