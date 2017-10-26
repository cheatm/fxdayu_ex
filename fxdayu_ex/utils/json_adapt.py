# encoding:utf-8

from itertools import chain
from datetime import datetime
import json


class JSONAdaptor:

    DIRECT = ()
    ENUMS = ()

    def to_json(self):
        dct = dict(
            chain(((attr, getattr(self, attr)) for attr in self.DIRECT),
                  ((name, getattr(self, name).value) for name, en in self.ENUMS))
        )

        return json.dumps(dct)

    @classmethod
    def from_json(cls, js):
        dct = json.loads(js)
        for name, _type in cls.ENUMS:
            dct[name] = _type(dct[name])

        return cls(**dct)