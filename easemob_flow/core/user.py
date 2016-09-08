from easemob_flow.util.lang import to_str
from easemob_flow.util.time import common_fmt_dt


class Role:

    """角色
    """

    def __init__(self, id_, name, description):
        self.id = id_
        self.name = name
        self.description = description

    def __repr__(self):
        return to_str(self, "id", "name", "description")

    def __str__(self):
        return self.__repr__()


class User:

    """用户
    """

    def __init__(self, id_, email, name, role, created_on, last_login_time):
        self.id = id_
        self.email = email
        self.name = name
        self.role = role
        self.created_on = created_on
        self.last_login_time = last_login_time

    def __repr__(self):
        return to_str(self, "id", "email", "name", "role",
                      ("created_on", common_fmt_dt),
                      ("last_login_time", common_fmt_dt))

    def __str__(self):
        return self.__repr__()
