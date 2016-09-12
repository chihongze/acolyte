from acolyte.testing import EasemobFlowTestCase
from acolyte.core.storage.user import UserDAO


class UserServiceTestCase(EasemobFlowTestCase):

    def setUp(self):
        self._user_service = self._("UserService")
        self._new_user_id_collector = []  # 用于收集测试所产生的新用户ID，在teardown中集中处理

    def testLogin(self):
        """测试登录操作
        """

        # 正常登录
        rs = self._user_service.login("chihz3800@163.com", "123456")
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data["id"], 1)

        # 账号密码不匹配
        rs = self._user_service.login("chihz3800@163.com", "654321")
        self.assertResultBadRequest(rs, "no_match")

    def testAddUser(self):
        """测试添加用户操作的各种情况
        """

        # 正常添加
        rs = self._user_service.add_user(
            email="chihongze@gmail.com",
            password="123456",
            name="SamChi",
            role=1,
            operator=1
        )
        self.assertResultSuccess(rs)
        self.assertTrue(rs.data.id > 0)
        self._new_user_id_collector.append(rs.data.id)

        # 邮件不符合规则
        rs = self._user_service.add_user(
            email="hhhhh",
            password="123456",
            name="SamChi",
            role=1,
            operator=1
        )
        self.assertResultBadRequest(rs, "email_invalid_format")

        # 重复注册
        rs = self._user_service.add_user(
            email="chihongze@gmail.com",
            password="654321",
            name="Jackson",
            role=1,
            operator=1
        )
        self.assertResultBadRequest(rs, "email_exist")

        # 指定一个不存在的角色
        rs = self._user_service.add_user(
            email="xiaoze@gmail.com",
            password="789101",
            name="Jackson",
            role=10000,
            operator=1
        )
        self.assertResultBadRequest(rs, "role_not_found")

        # 指定一个不存在的operator
        rs = self._user_service.add_user(
            email="xiaoze@gmail.com",
            password="789101",
            name="Jackson",
            role=1,
            operator=10000
        )
        self.assertResultBadRequest(rs, "operator_not_found")

    def testCheckToken(self):
        """测试token检查操作
        """
        rs = self._user_service.login(
            "chihz3800@163.com", "123456")

        # 正常的token检测
        token = rs.data["token"]
        rs = self._user_service.check_token(token)
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data["id"], 1)
        self.assertEqual(rs.data["session_data"]["name"], "Sam")

        # 错误token检测
        rs = self._user_service.check_token("你们啊！naive！")
        self.assertResultBadRequest(rs, "invalid_token")

    def testLogout(self):
        """测试退出接口
        """
        rs = self._user_service.login(
            "chihz3800@163.com", "123456")
        self.assertResultSuccess(rs)

        token = rs.data["token"]

        rs = self._user_service.check_token(token)
        self.assertResultSuccess(rs)

        rs = self._user_service.logout(token)
        self.assertResultSuccess(rs)

        rs = self._user_service.check_token(token)
        self.assertResultBadRequest(rs, "invalid_token")

    def tearDown(self):
        user_dao = UserDAO(self._("db"))
        if self._new_user_id_collector:
            user_dao.delete_by_id(self._new_user_id_collector)
