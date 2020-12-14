from Py2SQL import Py2SQL


class A:
    a = str

    def __init__(self, a):
        self.a = a
        print('A')


class V:
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


class TestAttr2:
    float_attr = float
    dict_attr = dict()

    def __init__(self, float_attr, dict_attr):
        self.float_attr = float_attr
        self.dict_attr = dict_attr

class TestClass4(B):
    c = list()
    cc = str
    ccc = TestAttr2
    obj_a = V

    def __init__(self, c, cc, ccc):
        self.c = c
        self.cc = cc
        self.ccc = ccc





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
    #client.save_class(TestClass4)
    tatr = TestAttr2(12.33, {1,2,3})
    t = TestClass4([1,2,3], "fsdfsdf", tatr)
    client.save_object(t)
    client.find_object(t)
    client.db_disconnect()


Test()
