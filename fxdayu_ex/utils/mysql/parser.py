# encoding:utf-8
import re


class MysqlURLParser:

    PATTERN = "jdbc:mysql://(.*?)/(.*?)\?(.*?)$"

    def __init__(self, url):
        self.url = url
        self.match = re.search(self.PATTERN, url, re.S)
        self._dct = {}
        host, db, args = self.match.groups()
        self._address(host)
        self._db(db)
        self._arguments(args)

    def connect(self):
        import pymysql
        return pymysql.connect(**self._dct)

    @property
    def parsed(self):
        return self._dct.copy()

    def _address(self, ads):
        host, port = ads.split(":")
        self._dct["host"] = host
        self._dct["port"] = int(port)

    def _db(self, db):
        self._dct['database'] = db

    def _arguments(self, args):
        for arg in args.split("&"):
            key, value = arg.split("=")
            self._dct[key] = value

if __name__ == '__main__':
    con = MysqlURLParser("jdbc:mysql://localhost:3306/broker?user=root&password=fxdayu").connect()
    cursor = con.cursor()
    cursor.execute("show tables")
    print(cursor.fetchall())