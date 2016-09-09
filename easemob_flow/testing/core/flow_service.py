from easemob_flow.core.service import Result
from easemob_flow.testing import EasemobFlowTestCase
from easemob_flow.util.json import to_json


class FlowServiceTestCase(EasemobFlowTestCase):

    def setUp(self):
        self.flow_service = self._service("flow_service")

    def test_get_all_flow_meta(self):
        result = self.flow_service.get_all_flow_meta()
        self.assertEqual(result.status_code, Result.STATUS_SUCCESS)
        print(to_json(result, indent=4 * ' '))
