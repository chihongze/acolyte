from acolyte.testing import EasemobFlowTestCase
from acolyte.testing.core.job import (
    EchoJob,
    OldManJob
)
from acolyte.core.mgr import DictBasedManager
from acolyte.exception import (
    ObjectAlreadyExistedException,
    ObjectNotFoundException
)


class DictBasedManagerTestCase(EasemobFlowTestCase):

    def setUp(self):
        self._mgr = DictBasedManager()

    def testRegister(self):
        echo_job = EchoJob()
        old_man_job = OldManJob()

        self._mgr.register(echo_job.name, echo_job)
        self._mgr.register(old_man_job.name, old_man_job)

        self.assertIsNotNone(self._mgr.get("echo"))
        self.assertIsNotNone(self._mgr.get("old_man"))

        with self.assertRaises(ObjectAlreadyExistedException):
            self._mgr.register(echo_job.name, echo_job)

    def test_get(self):
        with self.assertRaises(ObjectNotFoundException):
            self._mgr.get("unknown")
