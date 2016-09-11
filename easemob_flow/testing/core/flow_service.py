from easemob_flow.core.service import Result
from easemob_flow.testing import EasemobFlowTestCase


class FlowServiceTestCase(EasemobFlowTestCase):

    def setUp(self):
        self.flow_service = self._("FlowService")

    def test_get_all_flow_meta(self):
        result = self.flow_service.get_all_flow_meta()
        self.assertEqual(result.status_code, Result.STATUS_SUCCESS)
        self.print_json(result)

    def test_get_flow_meta_info(self):
        # 测试正常返回的情况
        result = self.flow_service.get_flow_meta_info("test_flow")
        self.assertEqual(result.status_code, Result.STATUS_SUCCESS)
        self.print_json(result)

        # 找不到指定的flow meta
        result = self.flow_service.get_flow_meta_info("heheda")
        self.assertEqual(result.status_code, Result.STATUS_BADREQUEST)
        self.assertEqual(result.reason, "flow_meta_not_exist")
        self.print_json(result)
