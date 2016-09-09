"""本模块包含跟用户相关的Facade接口
"""

from easemob_flow.core.service import AbstractService


class UserService(AbstractService):

    def __init__(self, service_container):
        super().__init__(service_container)

    def login(self, username, password):
        pass

    def check_token(self, token):
        pass

    def logout(self, token):
        pass

    def profile(self, user_id):
        pass
