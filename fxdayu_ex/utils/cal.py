# encoding:utf-8


class Rate:

    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def __mul__(self, other):
        return int(self.numerator * other /self.denominator)

    def __rmul__(self, other):
        return int(self.numerator * other /self.denominator)