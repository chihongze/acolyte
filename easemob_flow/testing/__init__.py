import fixtures
from easemob_flow.util.service_container import ServiceContainer
from easemob_flow.core.bootstrap import AbstractBootstrap
from easemob_flow.testing.core.mgr_define import (
    flow_meta_mgr,
    job_mgr
)
from easemob_flow.util import db
from easemob_flow.util.json import to_json
from easemob_flow.core.service import Result
from easemob_flow.core.flow_service import FlowService
from easemob_flow.core.user_service import UserService
from easemob_flow.core.job_service import JobService
from easemob_flow.core.flow_executor_service import FlowExecutorService


class UnitTestBootstrap(AbstractBootstrap):

    def __init__(self):
        super().__init__()

    def start(self, config):
        self.service_container = ServiceContainer()
        self._binding(config, self.service_container)

    def _binding(self, config, service_container):

        service_container.register(
            service_id="db",
            service_obj=self._init_db(config)
        )

        service_container.register(
            service_id="job_manager",
            service_obj=job_mgr
        )

        service_container.register(
            service_id="flow_meta_manager",
            service_obj=flow_meta_mgr
        )

        service_container.register_service(FlowService)
        service_container.register_service(UserService)
        service_container.register_service(JobService)
        service_container.register_service(FlowExecutorService)

        service_container.after_register()

    def _init_db(self, config):
        db_pool_cfg = config.get("db_pool", {})
        max_pool_size = db_pool_cfg.get("pool_size", 10)

        db_connect_cfg = config.get("db", {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "db": "easemob_flow",
        })

        return db.ConnectionPool(db_connect_cfg, max_pool_size)


_test_bootstrap = UnitTestBootstrap()
_test_bootstrap.start({})
_test_container = _test_bootstrap.service_container


class EasemobFlowTestCase(fixtures.TestWithFixtures):

    def _(self, service_id):
        """从容器中获取服务
        """
        global _test_container
        return _test_container.get_service(service_id)

    def print_json(self, obj):
        print(to_json(obj, indent=4 * ' '))

    def assertResultSuccess(self, result):
        self.assertEqual(result.status_code, Result.STATUS_SUCCESS)

    def assertResultBadRequest(self, result, reason):
        self.assertEqual(result.status_code, Result.STATUS_BADREQUEST)
        self.assertEqual(result.reason, reason)
