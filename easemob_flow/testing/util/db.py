import threading
from easemob_flow.testing import EasemobFlowTestCase
from easemob_flow.util.db import ConnectionPool


class DBPoolTestCase(EasemobFlowTestCase):

    """数据库连接池测试用例
    """

    def testCommonQuery(self):
        connect_config = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "db": "easemob_flow",
            "charset": "utf8"
        }

        count = 0
        cdt = threading.Condition()

        def query_():
            nonlocal count
            with pool.connection() as conn:
                with conn.cursor() as csr:
                    csr.execute("select 1", tuple())
                    result = csr.fetchone()
                    print(result)
                    self.assertEqual(result, {"1": 1})
                    with cdt:
                        count += 1
                        cdt.notify_all()

        pool = ConnectionPool(connect_config, max_pool_size=2)
        for _ in range(10):
            threading.Thread(target=query_).start()

        with cdt:
            while count < 10:
                cdt.wait()
