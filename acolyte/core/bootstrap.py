from abc import (
    ABCMeta,
    abstractmethod
)
from typing import Dict, Any
from acolyte.util import db
from acolyte.util.service_container import ServiceContainer
from acolyte.core.mgr import (
    job_manager,
    flow_meta_manager
)
from acolyte.core.flow_service import FlowService
from acolyte.core.user_service import UserService
from acolyte.core.job_service import JobService


class AbstractBootstrap(metaclass=ABCMeta):

    """Bootstrap类用于统一初始化启动应用所需要的组件和服务
    """

    def __init__(self):
        pass

    @abstractmethod
    def start(config):
        pass


class EasemobFlowBootstrap(AbstractBootstrap):

    """正式启动应用所需的Bootstrap
    """

    def __init__(self):
        super().__init__()

    def start(self, config: Dict[str, Dict[str, Any]]):
        """在这里对各种组件进行初始化
           :param config: 配置数据，字典套字典什么的
        """

        # 初始化数据库连接池
        db_pool_cfg = config.get("db_pool", {})
        max_pool_size = db_pool_cfg.get("pool_size", 10)

        db_connect_cfg = config.get("db", {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "db": "easemob_flow",
        })

        connection_pool = db.ConnectionPool(db_connect_cfg, max_pool_size)
        self._pool = connection_pool

        self._service_container = ServiceContainer()
        self._service_binding(self._service_container)

    @property
    def service_container(self):
        return self._service_container

    def _service_binding(self, service_container: ServiceContainer):
        """将服务绑定到注册容器
        """

        service_container.register(
            service_id="db",
            service_obj=self._pool
        )

        service_container.register(
            service_id="job_manager",
            service_obj=job_manager,
            init_callback=lambda service_obj: service_obj.load()
        )

        service_container.register(
            service_id="flow_meta_manager",
            service_obj=flow_meta_manager,
            init_callback=lambda service_obj: service_obj.load()
        )

        # 注册各种Service
        service_container.register_service(FlowService)
        service_container.register_service(UserService)
        service_container.register_service(JobService)

        service_container.after_register()
