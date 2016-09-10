"""本模块包含跟用户相关的Facade接口
"""

from easemob_flow.core.service import AbstractService, Result


class UserService(AbstractService):

    def __init__(self, service_container):
        super().__init__("user_service", service_container)

    def login(self, email: str, password: str) -> Result:
        pass

    def register(self, email: str, password: str) -> Result:
        pass

    def check_token(self, token: str) -> Result:
        pass

    def logout(self, token: str) -> Result:
        pass

    def profile(self, user_id: int) -> Result:
        pass
