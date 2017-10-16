# encoding:utf-8


class AbstractAccount(object):

    def send_order(self, order):
        raise NotImplementedError("Should implement method send_order")

    def cancel_order(self, orderID):
        raise NotImplementedError("Should implement method cancel_order")

    def get_order(self, orderID):
        raise NotImplementedError("Should implement method get_order")

    def get_position(self, code):
        raise NotImplementedError("Should implement method get_position")

    @property
    def cash(self):
        raise NotImplementedError("Should implement method cash")

    @property
    def positions(self):
        raise NotImplementedError("Should implement method positions")


