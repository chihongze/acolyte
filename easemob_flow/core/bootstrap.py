from easemob_flow.util import db
from easemob_flow.core.mgr import (
    job_manager,
    flow_meta_manager
)


def start(config):
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
    db.pool = connection_pool

    # 初始化FlowMetaManager
    job_manager.load()

    # 初始化JobMetaManager
    flow_meta_manager.load()
