from acolyte.testing import EasemobFlowTestCase
from acolyte.core.storage.user import UserDAO


class UserDAOTestCase(EasemobFlowTestCase):

    def setUp(self):
        self._dao = UserDAO(self._service("db"))
