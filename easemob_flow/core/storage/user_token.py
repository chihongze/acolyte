import datetime
import simplejson as json
from easemob_flow.core.storage import AbstractDAO


def _session_data_mapper(result):
    return {
        "id": result["id"],
        "session_data": json.loads(result["session_data"])
    }


class UserTokenDAO(AbstractDAO):

    def __init__(self, db):
        super().__init__(db)

    def upsert_token(self, user_id, token):
        """如果用户ID不存在，则插入新纪录
           如果已经存在，那么更新token
        """
        now = datetime.datetime.now()
        return self._db.execute((
            "insert into user_token ("
            "id, token, session_data, created_on) values ("
            "%s, %s, '{}', %s) on duplicate key update "
            "token = %s, session_data = '{}', created_on = %s"
        ), (user_id, token, now, token, now))

    def query_token_by_id(self, user_id) -> str:
        return self._db.query_one_field((
            "select token from user where id = %s"
        ), (user_id,))

    def query_session_data(self, token):
        global _session_data_mapper
        return self._db.query_one(
            "select id, session_data from user_token where token = %s",
            (token,), _session_data_mapper)

    def save_session_data(self, token, **kwds):
        session_data_rs = self.query_session_data(token)
        if session_data_rs is None:
            return
        session_data = session_data_rs["session_data"]
        session_data.update(kwds)
        self._db.execute((
            "update user_token set session_data = %s where "
            "token = %s limit 1"
        ), (json.dumps(session_data), token))

    def delete_by_token(self, token):
        self._db.execute(
            "delete from user_token where token = %s", (token,))
