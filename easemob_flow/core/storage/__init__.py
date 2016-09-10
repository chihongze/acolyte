from abc import ABCMeta


class AbstractDAO(metaclass=ABCMeta):

    def __init__(self, db_pool):
        self._db = db_pool
