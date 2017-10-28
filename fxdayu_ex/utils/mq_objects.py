import pika
from pika.channel import Channel
from fxdayu_ex.utils.rbmq import get_con


class RabbitObject(object):

    def callback(self, *args, **kwargs):
        pass


class RabbitExchange(object):

    def __init__(self,
                 exchange=None,
                 exchange_type='direct',
                 passive=False,
                 durable=False,
                 auto_delete=False,
                 internal=False,
                 nowait=False,
                 arguments=None):
        self.channel = None
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.passive = passive
        self.durable = durable
        self.auto_delete = auto_delete
        self.internal = internal
        self.nowait = nowait
        self.arguments = arguments

    def callback(self, frame):
        print(frame)

    def on_channel_open(self, channel):
        self.channel = channel
        channel.exchange_declare(self.callback,
                                 self.exchange,
                                 self.exchange_type,
                                 self.passive,
                                 self.durable,
                                 self.auto_delete,
                                 self.internal,
                                 self.nowait,
                                 self.arguments)

    def publish(self, routing_key, body,
                      properties=None,
                      mandatory=False,
                      immediate=False):
        if self.is_open:
            self.channel.basic_publish(
                self.exchange,
                routing_key, body,
                properties=None,
                mandatory=False,
                immediate=False
            )

    @property
    def is_open(self):
        return self.channel is not None and self.channel.is_open


class RabbitQueue(object):

    def __init__(self,
                 queue='',
                 passive=False,
                 durable=False,
                 exclusive=False,
                 auto_delete=False,
                 nowait=False,
                 arguments=None,
                 consumer=None,
                 bind=None):
        self.queue = queue
        self.passive = passive
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.nowait = nowait
        self.arguments = arguments
        self.channel = None
        self.consumer_tag = None
        self.consumer_callback = None
        self._consumer = self.consumer_wrap(consumer)
        self._bind = self.bind_wrap(bind)

    def consumer_wrap(self, consumer):
        consumer.queue = self.queue
        if consumer.consumer_tag is None:
            consumer.consumer_tag = consumer.queue
        return consumer

    def bind_wrap(self, bind):
        bind.queue = self.queue
        return bind

    def on_queue_open(self, method):
        print(method)
        self.queue = method.method.queue
        if self._consumer is not None:
            self.consume(self._consumer)
        if self._bind is not None:
            self.bind(self._bind)

    def on_channel_open(self, channel):
        self.channel = channel
        self.channel.queue_declare(
            self.on_queue_open,
            self.queue,
            self.passive,
            self.durable,
            self.exclusive,
            self.auto_delete,
            self.nowait,
            self.arguments
        )

    def consume(self, consumer):
        if self.is_open:
            self.channel.basic_consume(
                consumer.callback,
                consumer.queue,
                consumer.no_ack,
                consumer.exclusive,
                consumer.consumer_tag,
                consumer.arguments
            )

    @property
    def is_open(self):
        return self.channel is not None and self.channel.is_open

    def bind(self, bind):
        if self.is_open:
            self.channel.queue_bind(
                bind.callback,
                bind.queue,
                bind.exchange,
                bind.routing_key,
                bind.nowait,
                bind.arguments
            )


class RabbitConsumer(object):

    def __init__(self,
                 callback,
                 queue="",
                 no_ack=False,
                 exclusive=False,
                 consumer_tag=None,
                 arguments=None):
        self.queue = queue
        self.callback = callback
        self.no_ack = no_ack
        self.exclusive = exclusive
        self.consumer_tag = consumer_tag
        self.arguments = arguments


class BindQueue(object):

    def __init__(self, queue="", exchange="",
                       routing_key=None,
                       nowait=False,
                       arguments=None):
        self.queue = queue
        self.exchange = exchange
        self.routing_key = None
        self.nowait = False
        self.arguments = None

    def callback(self, method):
        print(method)


class RabbitStructure(object):

    def __init__(self, connection, exchanges, queues):
        self.connection = connection
        self.exchanges = exchanges
        self.queues = queues
        self.channel = None
        connection.add_on_open_callback(self.on_connection_open)

    def on_connection_open(self, connection):
        self.channel = self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        for name, rbex in self.exchanges.items():
            rbex.on_channel_open(self.channel)
        for name, rbq in self.queues.items():
            rbq.on_channel_open(self.channel)


def callback(*args):
    print(*args, sep="\n")


if __name__ == '__main__':
    connection = get_con("amqp://xinge:fxdayu@localhost:5672")

    structure = RabbitStructure(
        connection,
        {"Test": RabbitExchange("Test", "direct")},
        {"New": RabbitQueue("New", auto_delete=True,
                            consumer=RabbitConsumer(callback, no_ack=True),
                            bind=BindQueue(routing_key="New"))}
    )
    connection.ioloop.start()