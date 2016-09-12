from acolyte.core.context import MySQLContext
from acolyte.testing import EasemobFlowTestCase


class MySQLContextTestCase(EasemobFlowTestCase):

    def setUp(self):
        self._flow_ctx = MySQLContext(
            self._("FlowExecutorService"), self._("db"), 100086)

    def testCommonOperation(self):
        """测试MySQLContext的各种常规操作
        """

        self._flow_ctx["id"] = 100
        self._flow_ctx["name"] = "Sam"

        self.assertEqual(self._flow_ctx["id"], '100')
        self.assertEqual(self._flow_ctx["name"], "Sam")

        self.assertEqual(len(self._flow_ctx), 2)

        del self._flow_ctx["id"]
        self.assertIsNone(self._flow_ctx["id"])

    def tearDown(self):
        self._flow_ctx.destroy()
