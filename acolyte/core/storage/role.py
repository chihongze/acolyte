from acolyte.core.user import Role
from acolyte.core.storage import AbstractDAO


def _mapper(result):
    return Role(
        id_=result["id"],
        name=result["name"],
        description=result["description"]
    )


class RoleDAO(AbstractDAO):

    def __init__(self, db):
        super().__init__(db)

    def query_role_by_id(self, id_):
        return self._db.query_one(
            "select * from role where id = %s", (id_,), _mapper)
