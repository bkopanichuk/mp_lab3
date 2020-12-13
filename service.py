from Py2SQL import Py2SQL

class A:
    a = str

    def __init__(self, a):
        self.a = a
        print('A')


class B(A):
    b = int

    def __init__(self, a, b):
        super().__init__(a)
        self.b = b
        print('B')


class H(B):
    c = list()
    cc = str
    obj_a = A

    def __init__(self, a, b, c, cc):
        super().__init__(a, b)
        self.c = c
        self.cc = cc
        print('C')


class TestAttr:
    float_attr = float
    dict_attr = dict()

    def __init__(self, float_attr, dict_attr):
        self.float_attr = float_attr
        self.dict_attr = dict_attr

def Test():
    db = {
        "HOST": "hattie.db.elephantsql.com",
        "NAME": "zujspmed",
        "USER": "zujspmed",
        "PASSWORD": "HCM5jII1mMgGnMric4zeIlSl1UfVINuc",
        "PORT": "5432"
    }

    client = Py2SQL()
    client.db_connect(db=db)
    print(client.db_engine())
    print(client.db_size())
    print(client.db_tables())
    print(client.db_name())
    client.save_class(H)
    client.db_disconnect()

Test()