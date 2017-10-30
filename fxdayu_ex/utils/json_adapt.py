# encoding:utf-8

from itertools import chain
from datetime import datetime
import json


class JSONAdaptor:

    DIRECT = ()
    ENUMS = ()

    def to_dict(self):
        return dict(
            chain(((attr, getattr(self, attr)) for attr in self.DIRECT),
                  ((name, getattr(self, name).value) for name, en in self.ENUMS))
        )

    @classmethod
    def from_dict(cls, dct):
        dct = dct.copy()
        for name, _type in cls.ENUMS:
            dct[name] = _type(dct[name])

        return cls(**dct)

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, js):
        return cls.from_dict(json.loads(js))