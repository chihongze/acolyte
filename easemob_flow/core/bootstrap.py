from abc import (
    ABCMeta,
    abstractmethod
)
from easemob_flow.util import db
from easemob_flow.util.service_container import ServiceContainer
from easemob_flow.core.mgr import (
    job_manager,
    flow_meta_manager
)
from easemob_flow.core.flow_service import FlowService


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

    def start(self, config):
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
            "db": "easemob_flow",
        })

        connection_pool = db.ConnectionPool(db_connect_cfg, max_pool_size)
        self._pool = connection_pool

        service_container = ServiceContainer()
        self._service_binding(service_container)

    def _service_binding(self, service_container):
        """将服务绑定到注册容器
        """

        service_container.register(
            service_id="db_pool",
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

        service_container.register(
            service_id="flow_service",
            service_obj=FlowService(service_container)
        )

        service_container.after_register()
