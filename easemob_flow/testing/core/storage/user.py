from easemob_flow.testing import EasemobFlowTestCase
from easemob_flow.core.storage.user import UserDAO


class UserDAOTestCase(EasemobFlowTestCase):

    def setUp(self):
        self._dao = UserDAO(self._service("db"))
