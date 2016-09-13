from acolyte.testing import EasemobFlowTestCase
from acolyte.core.storage.flow_template import FlowTemplateDAO
from acolyte.core.storage.flow_instance import FlowInstanceDAO


class FlowExecutorServiceTestCase(EasemobFlowTestCase):

    def setUp(self):
        self._db = self._("db")
        self._flow_exec = self._("FlowExecutorService")
        self._flow_service = self._("FlowService")
        self._flow_tpl_dao = FlowTemplateDAO(self._db)
        self._flow_instance_dao = FlowInstanceDAO(self._db)

        self._flow_tpl_id_collector = []
        self._flow_instance_id_collector = []

        # 创建一个flow template供测试使用
        bind_args = {
            "echo": {
                "trigger": {
                    "b": 2
                },
                "finish": {
                    "c": 3
                },
                "stop": {
                    "d": 12.34,
                    "e": 12
                }
            }
        }
        rs = self._flow_service.create_flow_template(
            flow_meta_name="test_flow",
            name="sam_test",
            bind_args=bind_args,
            max_run_instance=1,
            creator=1
        )
        self._tpl_id = rs.data.id

        self._flow_tpl_id_collector.append(self._tpl_id)

    def testStartFlow(self):
        """测试启动flow实例
        """

        # 正常启动的情况
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": 5, "y": 6}
        )
        self.assertResultSuccess(rs)
        self.assertTrue(rs.data.id > 0)
        self._flow_instance_id_collector.append(rs.data.id)

        # 使用一个不存在的tpl
        rs = self._flow_exec.start_flow(
            flow_template_id=100086,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": 5, "y": 6}
        )
        self.assertResultBadRequest(rs, "invalid_flow_template")

        # 不合法的initiator
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=100086,
            description="测试flow instance",
            start_flow_args={"x": 5, "y": 6}
        )
        self.assertResultBadRequest(rs, "invalid_initiator")

        # 不合法的start参数
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": "aaaa", "y": 6}
        )
        self.assertResultBadRequest(rs, "start.x_invalid_type")

        # 同时运行多个实例
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": "5", "y": 6}
        )
        self.assertResultBadRequest(rs, "too_many_instance")

    def tearDown(self):
        if self._flow_tpl_id_collector:
            self._flow_tpl_dao.delete_by_id(self._flow_tpl_id_collector)
        if self._flow_instance_id_collector:
            self._flow_instance_dao.delete_by_instance_id(
                self._flow_instance_id_collector)
