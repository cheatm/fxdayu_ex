# encoding:utf-8
from itertools import chain


class MysqlTable:

    CREATE = "CREATE TABLE IF NOT EXISTS `%s`(%s);"
    INSERT = "INSERT INTO `%s` %s VALUES %s;"
    WHERE = "WHERE %s ;"
    SELECT = "SELECT %s from %s %s"
    ALTER = "ALTER TABLE %s %s;"
    UPDATE = "UPDATE %s %s %s %s"
    DELETE = "DELETE FROM %s %s"

    def __init__(self, name, *columns, **kwargs):
        self.name = name
        self.args = tuple(chain(
            columns,
            (("_last", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),)
        ))
        self.kwargs = kwargs
        self.columns = dict(columns)

    @property
    def create(self):
        return self.CREATE % (
            self.name,
            ", ".join(chain(
                self._columns(),
                self.kwargs.get("index", tuple()),
                self.kwargs.get("other", tuple())
            ))
        )

    @property
    def drop(self):
        return "DROP table %s" % self.name

    def insert(self, **kwargs):
        keys = "(%s)" % ", ".join(kwargs.keys())
        values = str(tuple(kwargs.values()))
        if len(kwargs) == 1:
            values = values[:-2]+')'

        return self.INSERT % (
            self.name,
            keys,
            values
        )

    def update(self, how="SET", where=None, **kwargs):
        if where is None:
            where = ";"
        else:
            where = self.where(where)

        return self.UPDATE % (self.name, how, self._join(**kwargs), where)

    @staticmethod
    def _join(**kwargs):
        return ", ".join(("%s=%s" % item for item in kwargs.items()))

    def select(self, fields='*', where=None):
        if where is None:
            where = ";"
        else:
            where = self.where(where)
        return self.SELECT % (fields, self.name, where)

    def where(self, args):
        if isinstance(args, str):
            return self.WHERE % args
        return self.WHERE % " AND ".join(args)

    def alter(self, query):
        return self.ALTER % (self.name, query)

    def delete(self, *where):
        return self.DELETE % (
            self.name,
            self.where(*where)
        )

    def _columns(self):
        for item in self.args:
            yield "%s %s" % item
