from threading import Thread
from queue import Queue, Empty


class Consumer(Thread):

    def __init__(self, queue, timeout):
        self.queue = queue
        self.timeout = timeout
        self._running = False
        super(Consumer, self).__init__()

    def start(self):
        if not self._running:
            self._running = True
            super(Consumer, self).start()

    def run(self):
        while self._running:
            try:
                quest = self.queue.get(timeout=self.timeout)
            except Empty as e:
                self.handle_empty(e)
            else:
                self.handle(quest)

    def handle(self, quest):
        pass

    def handle_empty(self, e):
        pass


class Engine(Consumer):

    def __init__(self):
        super(Engine, self).__init__(Queue(), 3)
        self.handlers = {}

    def __setitem__(self, key, value):
        self.handlers[key] = value

    def __getitem__(self, item):
        return self.handlers[item]

    def pop_handler(self, key):
        return self.handlers.pop(key, None)

    def handle(self, event):
        # try:
            self.handlers[event.type](event)
        # except Exception as e:
        #     self.handle_exception(e)

    def put(self, event):
        self.queue.put(event)

    def handle_exception(self, e):
        print(e)

    def queue_empty(self, e):
        pass


class Event:

    type = 0


class TickEvent(Event):

    type = 1

    def __init__(self, tick):
        self.tick = tick


class ReqEvent(Event):

    type = 2

    def __init__(self, req):
        self.req = req


class RespEvent(Event):

    type = 3

    def __init__(self, resp):
        self.resp = resp