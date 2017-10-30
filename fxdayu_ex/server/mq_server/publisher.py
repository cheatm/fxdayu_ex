import json
from queue import Queue
from pika import BasicProperties
from fxdayu_ex.server.frame.engine import Consumer


class ClientRespPublisher(Consumer):

    def __init__(self, rb_exchange):
        self.rb_exchange = rb_exchange
        super(ClientRespPublisher, self).__init__(Queue(), 5)

    def handle(self, quest):
        resp = quest.to_dict()
        try:
            resp = json.dumps({"type": quest.__class__.__name__, "data": resp})
        except:
            pass
        else:
            self.response(resp, quest.accountID)

    def response(self, body, accountID):
        self.rb_exchange.publish("", body, BasicProperties(headers={"accountID": accountID}))

