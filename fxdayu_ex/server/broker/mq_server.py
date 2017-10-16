from fxdayu_ex.server.broker.engine import BrokerServer
from threading import Thread
from pika import TornadoConnection, URLParameters
from pika.channel import Channel


class MQBrokerServer(BrokerServer):

    def __init__(self, connection, listen="BrokerServer"):
        self.channel = None
        self.listen = listen
        if isinstance(connection, TornadoConnection):
            self.connection = connection
            connection.channel(self.on_channel_open)

        else:
            raise TypeError("Type of connection should be TornadoConnection")

    def on_channel_open(self, channel):
        self.channel = channel
        # channel.basic_consume(self.consumer_callback, self.listen, True)


    def consumer_callback(self, channel, deliver, properties, body):
        print(body)

    def on_message(self, message):
        pass

    def send_message(self, message):
        pass

    # def run(self):
    #     self.connection.ioloop.start()

def get_open_con():
    con = TornadoConnection(URLParameters("amqp://xinge:fxdayu@localhost:5672"))
    Thread(target=con.ioloop.start).start()
    while not con.is_open:
        pass
    else:
        return con


if __name__ == '__main__':

    MQBrokerServer(get_open_con())

