# encoding:utf-8


class ReqEngine(object):
    """
    This engine is driven by client requests.
    """

class BrokerServer(object):

    def send_message(self, message):
        raise NotImplementedError("Should implement method send_message")

    def on_message(self, message):
        raise NotImplementedError("Should implement method on_message")
