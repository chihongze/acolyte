import datetime


class Role:

    """角色
    """

    def __init__(self, id_: int, name: str, description: str):
        self.id = id_
        self.name = name
        self.description = description


class User:

    """用户
    """

    def __init__(self, id_: int, email: str,
                 name: str, role: int,
                 created_on: datetime.datetime,
                 last_login_time: datetime.datetime):
        self.id = id_
        self.email = email
        self.name = name
        self.role = role
        self.created_on = created_on
        self.last_login_time = last_login_time
