from fxdayu_ex.utils.rbmq import MQExchangeConstructor
import json
from pika.channel import Channel


class MQClientInstance(MQExchangeConstructor):

    def __init__(self, connection, listen, publish, accountID):
        self.accountID = accountID
        self.publish = publish
        super(MQClientInstance, self).__init__(connection, listen)
        self.handlers = {}

    def add(self, name, handler):
        self.handlers[name] = handler

    def on_connection_open(self, connection):
        self.channel = connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        self.connect_req()
        self.connect_resp()

    def connect_req(self):
        self.channel.exchange_declare(self.on_publish_declare, self.publish)

    def on_publish_declare(self, *args):
        pass

    def connect_resp(self):
        self.channel.exchange_declare(self.on_consume_declare, self.exchange, "headers")

    def on_consume_declare(self, *args):
        self.channel.queue_declare(self.on_queue_open, self.accountID)

    def on_queue_open(self, method):
        self.channel.queue_bind(None, self.accountID, self.exchange, "", arguments={"accountID": self.accountID})

    def on_queue_bind(self, method):
        self.channel.basic_consume(self.consumer_callback, self.accountID, consumer_tag=self.accountID)

    def consumer_callback(self, channel, method, properties, body):
        self.on_exchange_callback(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def on_exchange_callback(self, message):
        try:
            objects = json.loads(message)
        except Exception as e:
            self.load_message_error(message, e)
        else:
            for name, js in objects.items():
                self.handlers[name](js)
        
    def load_message_error(self, message, e):
        pass