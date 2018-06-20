import random
from .Client import *


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)
        return cls._instance


# Make sure it is singleton
class HashMaker(Singleton):
    """docstring for HashMaker"""

    def __init__(self):
        pass

    def hash_user(self):
        value = (random.randint(0, 100000000) % 100000)
        if self.check_user_exist(value):
            return self.hash_user()
        else:
            return value

    def hash_task(self):
        value = (random.randint(0, 100000000) % 100000)
        if self.check_task_exist(value):
            return self.hash_task()
        else:
            return value

    def hash_graph(self):
        value = (random.randint(0, 100000000) % 100000)
        if self.check_graph_exist(value):
            return self.hash_graph()
        else:
            return value

    def check_user_exist(self, ID, table='User'):
        predicate = " `user_ID` = " + '"' + str(ID) + '"'
        result = select('*', table, predicate)
        if len(result) == 0:
            return False
        else:
            return True

    def check_user_name_exist(self, account):
        predicate = " `user_name` = " + '"' + str(account) + '"'
        result = select('*', 'User', predicate)
        if len(result) == 0:
            return False
        else:
            return True

    def check_task_exist(self, ID, table='Node'):
        predicate = " `task_ID` = " + '"' + str(ID) + '"'
        result = select('*', table, predicate)
        if len(result) == 0:
            return False
        else:
            return True

    def check_graph_exist(self, ID, table='DAG'):
        predicate = " `graph_ID` = " + '"' + str(ID) + '"'
        result = select('*', table, predicate)
        if len(result) == 0:
            return False
        else:
            return True


def sha1_encode(password):
    result = hashlib.sha1()
    result.update(password.encode())
    return result.hexdigest()
