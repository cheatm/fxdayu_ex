from fxdayu_ex.utils.rbmq import MQHeaderPublisher
from fxdayu_ex.server.frame.engine import Consumer
from queue import Queue


ID = "accountID"


class ClientHeaderPublisher(MQHeaderPublisher):

    def send(self, storage):
        body = storage.to_json()
        headers = {ID: storage.accountID}
        self.publish(body, headers)


class ClientResponse(Consumer):

    def __init__(self, publisher):
        self.publisher = publisher
        super(ClientResponse, self).__init__(Queue(), 3)

    def handle(self, quest):
        self.publisher.send(quest)
