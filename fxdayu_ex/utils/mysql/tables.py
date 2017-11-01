from fxdayu_ex.utils.mysql.objects import MysqlTable


class InstanceTable(MysqlTable):

    def insert(self, instance):
        dct = instance.to_dict()
        del dct['cls']
        return MysqlTable.insert(self, **dct)


class CashTable(InstanceTable):

    def __init__(self):
        super(CashTable, self).__init__(
            "cash",
            ("accountID", "INT UNIQUE NOT NULL"),
            ("available", "BIGINT DEFAULT 0"),
            ("frozen", "BIGINT DEFAULT 0"),
            index=("Index accountID_1 (accountID)",)
        )

    def update(self, cash):
        MysqlTable.update(
            self,
            where="accountID==%s" % cash.accountID,
            available=cash.available,
            frozen=cash.frozen
        )


class OrderTable(InstanceTable):

    def __init__(self):
        super(OrderTable, self).__init__(
            "orders",
            ("accountID", "INT NOT NULL"),
            ("orderID", "INT UNIQUE NOT NULL"),
            ("code", "CHAR(255)"),
            ("qty", "INT DEFAULT 0"),
            ("cumQty", "INT DEFAULT 0"),
            ("price", "INT DEFAULT 0"),
            ("orderType", "TINYINT"),
            ("bsType", "TINYINT"),
            ("orderStatus", "TINYINT"),
            ("frzAmt", "BIGINT DEFAULT 0"),
            ("frzFee", "INT DEFAULT 0"),
            ("cumAmt", "INT DEFAULT 0"),
            ("cumFee", "INT DEFAULT 0"),
            ("canceled", "INT DEFAULT 0"),
            ("reason", "TINYINT"),
            ("time", "DATETIME(6)"),
            ("cnfmTime", "DATETIME(6)"),
            ("info", "VARCHAR(1023)"),
            index=("Index accountID_1 (accountID)",
                   "Index orderID_1 (orderID)")
        )

    def update(self, order):
        return MysqlTable.update(
            self,
            where="orderID==%s" % order.orderID,
            orderStatus=order.orderStatus,
            cumQty=order.cumQty,
            frzAmt=order.frzAmt,
            frzFee=order.frzFee,
            canceled=order.canceled,
            reason=order.reason,
            cnfmTime=order.cnfmTime
        )


class TradeTable(InstanceTable):

    def __init__(self):
        super(TradeTable, self).__init__(
            "trades",
            ("accountID", "INT NOT NULL"),
            ("orderID", "INT NOT NULL"),
            ("tradeID", "INT UNIQUE NOT NULL"),
            ("code", "CHAR(255)"),
            ("qty", "INT DEFAULT 0"),
            ("orderType", "TINYINT"),
            ("bsType", "TINYINT"),
            ("fee", "INT DEFAULT 0"),
            ("orderStatus", "TINYINT"),
            ("time", "DATETIME(6)"),
        )


class PositionTable(InstanceTable):
    def __init__(self):
        super(PositionTable, self).__init__(
            'positions',
            ("accountID", "INT NOT NULL"),
            ("code", "CHAR(255)"),
            ("origin", "INT DEFAULT 0"),
            ("available", "INT DEFAULT 0"),
            ("frozen", "INT DEFAULT 0"),
            ("today", "INT DEFAULT 0"),
            ("todaySell", "INT DEFAULT 0"),
            index=("Index accountID_1 (accountID)",)
        )

    def update(self, position):
        return MysqlTable.update(
            self,
            where=("accountID==%s" % position.accountID, "code==%s" % position.code),
            available=position.available,
            frozen=position.frozen,
            today=position.today,
            todaySell=position.todaySell
        )


if __name__ == '__main__':
    from fxdayu_ex.utils.mysql.parser import MysqlURLParser
    from fxdayu_ex.module.instance import Order
    from datetime import datetime

    # con = MysqlURLParser("jdbc:mysql://localhost:3306/broker?user=root&password=fxdayu").connect()

    # cursor = con.cursor()
    # order = Order(123, 4245, "000001.XSHE", 1000, price=1000000,
    #               time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #               cnfmTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # dct = order.to_dict()
    # dct.pop("cls")
    # cursor.execute(OrderTable().insert(**dct))
    # con.commit()
