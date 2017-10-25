from threading import Thread
from queue import Queue, Empty



class Engine(Thread):

    def __init__(self):
        super(Engine, self).__init__()
        self.queue = Queue()
        self.handlers = {}
        self._running = False

    def __setitem__(self, key, value):
        self.handlers[key] = value

    def __getitem__(self, item):
        return self.handlers[item]

    def pop_handler(self, key):
        return self.handlers.pop(key, None)

    def start(self):
        if not self._running:
            self._running = True
        else:
            return

        super(Engine, self).start()

    def run(self):
        while self._running:
            try:
                event = self.queue.get(3)
            except Empty as e:
                self.queue_empty(e)
                continue

            try:
                self.handlers[event.type](event)
            except Exception as e:
                self.handle_exception(e)

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