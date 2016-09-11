import datetime
from easemob_flow.core.user import User
from easemob_flow.core.storage import AbstractDAO


def _mapper(result):
    result.pop("password")
    result["id_"] = result.pop("id")
    return User(**result)


class UserDAO(AbstractDAO):

    def __init__(self, db):
        super().__init__(db)

    def query_user_by_id(self, user_id):
        global _mapper
        return self._db.query_one((
            "select * from user where id = %s"
        ), (user_id,), _mapper)

    def is_email_exist(self, email):
        return self._db.query_one(
            "select id from user where email = %s", (email,))

    def insert_user(self, email, password, name, role):
        now = datetime.datetime.now()
        with self._db.connection() as conn:
            with conn.cursor() as csr:
                csr.execute((
                    "insert into user ("
                    "email, password, name, role, "
                    "created_on, last_login_time) values ("
                    "%s, %s, %s, %s, %s, %s)"
                ), (email, password, name, role, now, now))
                conn.commit()
                return User(csr.lastrowid,
                            email, name, role, now, now)

    def delete_by_id(self, user_id):
        if isinstance(user_id, list):
            holders = ",".join(("%s", ) * len(user_id))
            return self._db.execute(
                "delete from user where id in ({holders})".format(
                    holders=holders), user_id)
        else:
            return self._db.execute(
                "delete from user where id = %s", (user_id, ))

    def query_user_by_email_and_password(self, email, password):
        global _mapper
        return self._db.query_one((
            "select * from user "
            "where email = %s and password = %s"
        ), (email, password), _mapper)
