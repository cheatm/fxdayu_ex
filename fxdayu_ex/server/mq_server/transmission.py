from itertools import chain
from fxdayu_ex.module.enums import BSType, OrderType
from fxdayu_ex.module.request import ReqOrder, CancelOrder
from fxdayu_ex.module.storage import Cash, Order, Trade, Position


def dct2obj_cons(cls, directs, funcs):
    def dct2obj(dct):
        return cls(**dict(chain(
            ((name, dct[name]) for name in directs),
            ((name, func(dct[name])) for name, func in funcs)
        )))

    return dct2obj


def obj2dct_cons(directs, funcs):
    def obj2dct(obj):
        return dict(chain(
            ((name, getattr(obj, name)) for name in directs),
            ((name, func(getattr(obj, name))) for name, func in funcs),
        ))
    return obj2dct


def enum_value(ens):
    return ens.value


ACCOUNT_ID = "accountID"
CODE = "code"
QTY = "qty"
PRICE = "price"
ORD_TYPE = "orderType"
BS_TYPE = "bsType"
TIME = "time"
INFO = "info"


ro_direct = (ACCOUNT_ID, CODE, QTY, PRICE, TIME, INFO)
ro_func_d2o = ((ORD_TYPE, OrderType), (BS_TYPE, BSType))
ro_func_o2d = ((ORD_TYPE, enum_value), (BS_TYPE, enum_value))


dct2ro = dct2obj_cons(ReqOrder, ro_direct, ro_func_d2o)
ro2dct = obj2dct_cons(ro_direct, ro_func_o2d)


if __name__ == '__main__':
    # print(dct2ro({ACCOUNT_ID: 12, CODE: "000001.XSHE", QTY: 300, PRICE:0, ORD_TYPE: 1, BS_TYPE: 1, TIME: "", INFO: ""}))
    print(ro2dct(ReqOrder(orderType=OrderType.LIMIT, bsType=BSType.BUY)))

# def dct2ro(dct):
#     return ReqOrder(dct[ACCOUNT_ID], dct[CODE], dct[QTY], dct[PRICE],
#                     OrderType(dct[ORD_TYPE]), BSType(dct[BS_TYPE]),
#                     dct[TIME], dct[INFO])
#
#
# def ro2dct(req):
#     dct = {name: getattr(req, name) for name in ro_direct}
#     for name, func in ro_func.items():
#         dct[name] = func(getattr(req, name))
#     return dct
#
#
# ord_direct = ()
# ord_func = ()
#
#
# def dct2ord(dct):
#     return Order(**dict(chain(
#         ((name, dct[name]) for name in ord_direct),
#         ((name, func(dct[name])) for name, func in ord_func)
#     )))