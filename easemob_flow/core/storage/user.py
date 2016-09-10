from easemob_flow.core.storage import AbstractDAO


def _mapper(result):
    pass


class UserDAO(AbstractDAO):

    def __init__(self, db):
        super().__init__(db)

    def query_user_by_id(self, user_id):
        global _mapper
        return self._db.query_one((
            "select * from user where id = ?"
        ), (user_id,), _mapper)
