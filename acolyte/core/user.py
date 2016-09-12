class Role:

    """角色
    """

    def __init__(self, id_, name, description):
        self.id = id_
        self.name = name
        self.description = description


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
