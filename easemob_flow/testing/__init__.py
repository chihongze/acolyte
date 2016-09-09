import fixtures
from easemob_flow.util.service_container import ServiceContainer
from easemob_flow.core.bootstrap import AbstractBootstrap
from easemob_flow.testing.core.mgr_define import (
    flow_meta_mgr,
    job_mgr
)
from easemob_flow.core.flow_service import FlowService


class UnitTestBootstrap(AbstractBootstrap):

    def __init__(self):
        super().__init__()

    def start(self, config):
        self.service_container = ServiceContainer()
        self._binding(self.service_container)

    def _binding(self, service_container):

        service_container.register(
            service_id="job_manager",
            service_obj=job_mgr
        )

        service_container.register(
            service_id="flow_meta_manager",
            service_obj=flow_meta_mgr
        )

        service_container.register(
            service_id="flow_service",
            service_obj=FlowService(service_container)
        )

        service_container.after_register()

_test_bootstrap = UnitTestBootstrap()
_test_bootstrap.start({})
_test_container = _test_bootstrap.service_container


class EasemobFlowTestCase(fixtures.TestWithFixtures):

    def _service(self, service_id):
        """从容器中获取服务
        """
        global _test_container
        return _test_container.get_service(service_id)
