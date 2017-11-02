# encoding:utf-8
from fxdayu_ex.utils.rbmq.objects import RabbitExchange, RabbitQueue, RabbitStructure, RabbitConsumer, BindQueue
from fxdayu_ex.utils.rbmq.con import consumer_ack, consumer_no_ack


TICK = "Tick"
REQUEST = "ClientRequest"
RESPONSE = "ClientResponse"
ALL = "all"


def get_req_ex():
    return RabbitExchange(REQUEST, "fanout")


def get_resp_ex():
    return RabbitExchange(RESPONSE)


def get_tick_ex():
    return RabbitExchange(TICK, "headers")


def client_resp_queue(accountID, callback):
    return RabbitQueue(str(accountID),
                       consumer=RabbitConsumer(consumer_ack(callback)),
                       bind=BindQueue(exchange=RESPONSE, routing_key=str(accountID)))


def client_req_queue(callback):
    return RabbitQueue("request",
                       consumer=RabbitConsumer(consumer_ack(callback)),
                       bind=BindQueue(exchange=REQUEST))


def all_tick_queue(callback):
    return RabbitQueue(ALL, auto_delete=True,
                       consumer=RabbitConsumer(consumer_no_ack(callback), no_ack=True),
                       bind=BindQueue(exchange=TICK, arguments={}))