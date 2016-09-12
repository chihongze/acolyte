import time
import threading
from acolyte.testing import EasemobFlowTestCase
from acolyte.util.db import ConnectionPool


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

        cdt = threading.Condition()
        count = 0

        def _fight_for_lock(sleep_time):
            """锁争夺
            """
            nonlocal pool
            nonlocal count
            with pool.lock("nidaye"):
                print("Thread '{thread_name}' get the lock!".format(
                    thread_name=threading.currentThread().name))
                time.sleep(sleep_time)
                print("Thread '{thread_name}' release the lock!".format(
                    thread_name=threading.currentThread().name))
                with cdt:
                    count += 1
                    cdt.notify_all()

        for i in range(5):
            t = threading.Thread(target=_fight_for_lock, args=(0.5,))
            t.name = "hehe %d" % i
            t.start()

        with cdt:
            while count < 5:
                cdt.wait()
