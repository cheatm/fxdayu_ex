# encoding:utf-8
import logging
from fxdayu_ex.server.IO.structures import get_resp_ex, get_req_ex, client_resp_queue, REQUEST, RESPONSE
from fxdayu_ex.utils.rbmq.con import get_con
from fxdayu_ex.utils.rbmq.objects import RabbitStructure
from threading import Thread
from fxdayu_ex.client.IO.callback import ClientCallback


class ExRabbitConnection(Thread):

    def __init__(self, url, *callbacks):
        super(ExRabbitConnection, self).__init__(name='ExRabbitConnection')
        self.callbacks = {callback.accountID: callback for callback in callbacks}
        self.url = url
        self.connection = get_con(url)
        self.requester = get_req_ex()
        self.resp_queues = {callback.accountID: client_resp_queue(callback.accountID, callback.on_resp)
                            for callback in self.callbacks.values()}
        self.structure = RabbitStructure(
            self.connection,
            {REQUEST: self.requester,
             RESPONSE: get_resp_ex()},
            self.resp_queues
        )

    def start(self):
        super(ExRabbitConnection, self).start()
        while not self.requester.is_open:
            pass
        return 1

    def run(self):
        self.connection.ioloop.start()

    def request(self, req):
        try:
            req = req.to_json()
        except Exception as e:
            logging.warning("Dump %s fail: %s", req, e)
        else:
            self.requester.publish("", req)


if __name__ == '__main__':
    from fxdayu_ex.utils.logger import dict_initiate
    dict_initiate()
    connection = ExRabbitConnection("amqp://192.168.0.104:10009", ClientCallback(1))
    result = connection.start()
    print(result)