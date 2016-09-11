"""本模块包含跟用户相关的Facade接口
"""

import time
import random
from easemob_flow.util.validate import (
    IntField,
    StrField,
    check,
    BadReq
)
from easemob_flow.util.sec import sha1
from easemob_flow.core.service import AbstractService, Result
from easemob_flow.core.storage.user import UserDAO
from easemob_flow.core.storage.role import RoleDAO
from easemob_flow.core.storage.user_token import UserTokenDAO


class UserService(AbstractService):

    _TOKEN_SALT = "6f81900c31f7fd80bd"

    def __init__(self, service_container):
        super().__init__(service_container)

    def _after_register(self):
        self._db = self._("db")
        self._user_dao = UserDAO(self._db)
        self._role_dao = RoleDAO(self._db)
        self._user_token_dao = UserTokenDAO(self._db)

    @check(
        StrField("email", required=True),
        StrField("password", required=True)
    )
    def login(self, email: str, password: str) -> Result:
        """登录
        S1. 通过email和password检索用户
        S2. 创建并获取新的token
        S3. 存储相关用户数据到session_data
        """
        user = self._user_dao.query_user_by_email_and_password(
            email=email,
            password=sha1(password)
        )
        if user is None:
            raise BadReq("no_match")

        # do upsert
        new_token = self._gen_new_token(user.id)
        self._user_token_dao.upsert_token(user.id, new_token)

        # save user basic info to session data
        self._user_token_dao.save_session_data(
            new_token, name=user.name, email=user.email)

        return Result.ok(data={"id": user.id, "token": new_token})

    def _gen_new_token(self, user_id: int):
        """生成新token
           规则: sha1({用户ID}{时间戳}{随机数}{salt})
        """
        return sha1((
            "{user_id}"
            "{timestamp_int}"
            "{randnum}"
            "{salt}"
        ).format(
            user_id=user_id,
            timestamp_int=int(time.time()),
            randnum=random.randint(10000, 99999),
            salt=UserService._TOKEN_SALT))

    @check(
        StrField("email", required=True, regex=r'^[\w.-]+@[\w.-]+.\w+$'),
        StrField("password", required=True, min_len=6, max_len=20),
        StrField("name", required=True, max_len=10),
        IntField("role", required=True),
        IntField("operator", required=True)
    )
    def add_user(self, email: str, password: str,
                 name: str, role: int, operator: int) -> Result:
        """添加新用户
           S1. 检查邮箱是否存在
           S2. 检查角色是否存在
           S3. 检查operator是否有权限
           S4. 创建新用户
           :param email: 邮箱地址
           :param password: 密码，会经过sha1加密
           :param name: 姓名
           :param role: 角色编号
           :param operator: 操作者
        """

        # 检查是否已注册
        if self._user_dao.is_email_exist(email):
            raise BadReq("email_exist", email=email)

        # 检查角色是否合法
        if not self._role_dao.query_role_by_id(role):
            raise BadReq("role_not_found", role=role)

        # 检查操作者信息及权限
        operator_model = self._user_dao.query_user_by_id(operator)
        if operator_model is None:
            raise BadReq("operator_not_found")
        operator_role = self._role_dao.query_role_by_id(operator_model.role)
        if operator_role.name != "admin":
            raise BadReq("not_allow_operation")

        # 创建新用户
        new_user = self._user_dao.insert_user(
            email, sha1(password), name, role)
        return Result.ok(data=new_user)

    @check(StrField("token", required=True))
    def check_token(self, token: str) -> Result:
        """检查token
           S1. 查找token相关的用户信息
           S2. 返回token关联简单会话数据
        """
        session_data = self._user_token_dao.query_session_data(token)
        if session_data is None:
            raise BadReq("invalid_token")
        return Result.ok(data=session_data)

    def logout(self, token: str) -> Result:
        """退出
           S1. 直接从数据库中删除token记录
        """
        self._user_token_dao.delete_by_token(token)
        return Result.ok()

    def profile(self, user_id: int) -> Result:
        ...
