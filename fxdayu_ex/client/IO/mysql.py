from fxdayu_ex.utils.mysql.tables import CashTable, AccountTable
from fxdayu_ex.utils.mysql.parser import MysqlURLParser
from fxdayu_ex.module.record import CashRecord


class MysqlAccount:

    def __init__(self, url):
        self.parser = MysqlURLParser(url)
        self.connection = self.parser.connect()
        self.acc = AccountTable()
        self.cash =  CashTable()

    def create(self, available=0, info="", active=True):
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.acc.insert(info=info, active=int(active)))
            cursor.execute("SELECT accountID FROM accounts ORDER BY accountID DESC")
            accountID = cursor.fetchone()[0]
            cursor.execute(self.cash.insert(CashRecord(accountID, available)))
        except Exception as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()
            return accountID

    def remove(self, accountID):
        cursor = self.connection.cursor()
        try:
            condition = "accountID=%s" % accountID
            cursor.execute(self.acc.select("accountID", condition))
            result = cursor.fetchone()
            if result is None:
                raise ValueError("AccountID: %s not found" % accountID)
            cursor.execute(self.acc.delete(condition))
        except Exception as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

    def activate(self, *ids):
        cursor = self.connection.cursor()
        for accountID in ids:
            try:
                condition = "accountID=%s" % accountID
                cursor.execute(self.acc.update(
                    where=condition,
                    active=1
                ))
            except Exception as e:
                self.connection.rollback()
                raise e
        self.connection.commit()


    def deactivate(self, *ids):
        cursor = self.connection.cursor()
        for accountID in ids:
            try:
                condition = "accountID=%s" % accountID
                cursor.execute(self.acc.update(
                    where=condition,
                    active=0
                ))
            except Exception as e:
                self.connection.rollback()
                raise e
        self.connection.commit()


if __name__ == '__main__':
    acc=MysqlAccount("jdbc:mysql://localhost:3306/broker?user=root&password=fxdayu")
    acc.activate(1, 3, 5)