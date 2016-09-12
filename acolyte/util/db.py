import time
import pymysql
from queue import Queue
from contextlib import contextmanager


class ConnectionPool:

    """
    基于Queue的数据库连接池
    """

    def __init__(self, config, max_pool_size=20):
        self.config = config
        self.max_pool_size = max_pool_size
        self._initialize_pool()

    def _initialize_pool(self):
        self.pool = Queue(maxsize=self.max_pool_size)
        for _ in range(0, self.max_pool_size):
            conn = _PooledMySQLConnection(**self.config)
            self.pool.put_nowait(conn)

    @contextmanager
    def connection(self):
        #  returns a db instance when one is available else waits until one is
        connection = self.pool.get(True)
        yield connection
        self.return_connection(connection)

    def return_connection(self, db):
        return self.pool.put_nowait(db)

    def close_all(self):
        while not self.is_empty():
            self.pool.get().close()

    def is_empty(self):
        return self.pool.empty()

    def query_one(self, sql, args, mapper=None):

        def callback(cursor):
            nonlocal sql, args
            num = cursor.execute(sql, args)
            if num:
                return cursor.fetchone()
            return None
        result = self.cursor_callback(callback)
        if result is None:
            return result

        if mapper is None:
            return result
        return mapper(result)

    def query_one_field(self, sql, args):
        record = self.query_one(sql, args)
        if not record:
            return None
        return tuple(record.values())[0]

    def query_all(self, sql, args, mapper=None):

        def callback(cursor):
            nonlocal sql, args
            num = cursor.execute(sql, args)
            if num:
                return cursor.fetchall()
            return []

        results = self.cursor_callback(callback)

        if mapper is None:
            return results
        return [mapper(r) for r in results]

    def execute(self, sql, args):

        def callback(cursor):
            nonlocal sql, args
            num = cursor.execute(sql, args)
            return num
        row_num = self.cursor_callback(callback)
        return row_num

    def cursor_callback(self, callback):
        with self.connection() as conn:
            with conn.cursor() as cursor:
                rs = callback(cursor)
                conn.commit()
                return rs

    @contextmanager
    def lock(self, lock_key, wait_timeout=-1):
        """基于MySQL的分布式锁，详情请参见mysql的get_lock函数
           :param lock_key: 锁关键字，通过该关键字来标识一个锁
           :param wait_timeout: 等待超时时间，如果为负数，那么永不超时
        """
        with self.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("select get_lock(%s, %s)",
                               (lock_key, wait_timeout))
                yield
                cursor.execute("select release_lock(%s)", (lock_key,))


class _PooledMySQLConnection:

    """该类型对象表示一个被池化的连接
    """

    def __init__(self, host, port, user, password, db,
                 charset="utf8", cursorclass=pymysql.cursors.DictCursor,
                 ping_interval=60):

        self._connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            charset=charset,
            cursorclass=pymysql.cursors.DictCursor)
        self._last_ping = time.time()
        self._ping_interval = ping_interval

    def _ping(self):
        if time.time() - self._last_ping >= self._ping_interval:
            need_re_connect = False
            try:
                with self._connection.cursor() as csr:
                    csr.execute("SELECT 1", tuple())
                    result = csr.fetchone()
                    if not result:
                        need_re_connect = True
            except pymysql.err.OperationalError:
                need_re_connect = True

            if need_re_connect:
                self._connection.connect()

    def cursor(self):
        self._ping()
        return self._connection.cursor()

    def commit(self):
        return self._connection.commit()

    def close(self):
        return self._connection.close()

    def rollback(self):
        return self._connection.rollback()
