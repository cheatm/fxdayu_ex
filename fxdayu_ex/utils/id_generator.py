# encoding:utf-8
import time


class IDGenerator(object):

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError("Should implement method next")


class TimerIDGenerator(IDGenerator):

    def __init__(self, timestamp, multiple=100):
        self.last = 0
        self.multiple = multiple
        self.origin = int(timestamp * self.multiple)

    @classmethod
    def rule(cls, rule):
        timestamp, multiple = rule.split("*")
        return cls(int(timestamp), int(multiple))

    @classmethod
    def year(cls):
        from datetime import date

        return cls(time.mktime(date.today().replace(month=1, day=1).timetuple()))

    def __next__(self):
        return self.next()

    def next(self):
        num = int(time.time()*self.multiple) - self.origin
        if num > self.last:
            self.last = num
        else:
            self.last += 1

        return self.last


TimeRule = {"year": TimerIDGenerator.year()}


def get_timer_id(rule):
    try:
        return TimeRule[rule]
    except KeyError:
        return TimerIDGenerator.rule(rule)