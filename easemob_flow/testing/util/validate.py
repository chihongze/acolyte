import typing
from easemob_flow.testing import EasemobFlowTestCase
from easemob_flow.util.validate import (
    IntField,
    StrField,
    InvalidFieldException,
    BadReq,
    check,
)


class RuleTestCase(EasemobFlowTestCase):

    def testIntField(self):
        """测试IntField类型的规则
        """

        int_field = IntField("age", min_=6, max_=100)

        # 值正常的时候
        self.assertEqual(int_field(99), 99)
        self.assertEqual(int_field("10"), 10)

        # 类型不匹配
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            int_field("nidaye")
        self._assert_invalid_f(
            raise_ctx.exception, "age", "nidaye", "invalid_type", int)

        # 大小不匹配
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            int_field(-1)
        self._assert_invalid_f(
            raise_ctx.exception, "age", -1, "less_than_min", 6)
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            int_field(101)
        self._assert_invalid_f(
            raise_ctx.exception, "age", 101, "more_than_max", 100)

        # 自定义检查逻辑
        def _my_check(field_name, age):
            if age % 2 != 0:
                raise InvalidFieldException(
                    field_name, age, "invalid_age", "even")
        int_field = IntField("age", min_=6, max_=100, check_logic=_my_check)

        # 值正确的情况
        self.assertEqual(int_field(6), 6)
        self.assertEqual(int_field(100), 100)

        # 值不正确的情况
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            int_field(7)
        self._assert_invalid_f(
            raise_ctx.exception, "age", 7, "invalid_age", "even")

        # required but value is None
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            int_field(None)
        self._assert_invalid_f(raise_ctx.exception, "age", None, "empty", "")

        # not required and value is None
        int_rule = IntField("age", False, default=6)
        self.assertEqual(int_rule(None), 6)

    def testStrField(self):
        """测试StrField类型的规则
        """

        def _my_check(field_name, value):
            parts = value.split("@")[-1].split(".")
            if len(parts) != 2:
                raise InvalidFieldException(
                    field_name, value, "invalid_parts", 2)

        str_field = StrField(
            name="email",
            required=True,
            min_len=6,
            max_len=100,
            regex=r'^[\w.-]+@[\w.-]+.\w+$',
            check_logic=_my_check
        )

        # 正常检查
        self.assertEqual(str_field("chihz@163.com"), "chihz@163.com")

        # 太短
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            str_field("z@z.c")
        self._assert_invalid_f(
            raise_ctx.exception, "email", "z@z.c", "less_than_min_length", 6)

        # 太长
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            str_field("z@z." + "c" * 100)
        self._assert_invalid_f(
            raise_ctx.exception, "email", "z@z." + "c" * 100,
            "more_than_max_length", 100)

        # 不符合正则
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            str_field("nidayehehe")
        self._assert_invalid_f(raise_ctx.exception, "email",
                               "nidayehehe", "invalid_format",
                               r'^[\w.-]+@[\w.-]+.\w+$')

        # 不符合自定义的检查规则
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            str_field("a@b.c.d")
        self._assert_invalid_f(
            raise_ctx.exception, "email", "a@b.c.d", "invalid_parts", 2)

        # required but value is None
        with self.assertRaises(InvalidFieldException) as raise_ctx:
            str_field(None)
        self._assert_invalid_f(
            raise_ctx.exception, "email", None, "empty", "")

        # not requied and value is None
        str_rule = StrField("name", required=False, default="Jack")
        self.assertEqual(str_rule(None), "Jack")

    def _assert_invalid_f(self, exc, field_name, value, reason, expect):
        """assert InvalidFieldException
        """
        self.assertEqual(exc.field_name, field_name)
        self.assertEqual(exc.value, value)
        self.assertEqual(exc.reason, reason)
        self.assertEqual(exc.expect, expect)


class CheckDecoratorTestCase(EasemobFlowTestCase):

    """针对check decorator的测试
    """

    def setUp(self):
        self.messages = {
            "C/zh_CN": {
                "AService": {
                    "a": {
                    }
                },
                "BService": {
                    "b": {
                        "invalid_id": "不合法的ID值'{id}'"
                    }
                }
            }
        }

    def testCommon(self):
        """测试check decorator的常规使用
        """

        class AService:

            @check(
                IntField("id", required=True, min_=6, max_=100),
                StrField("name", required=True, min_len=3, max_len=20),
                StrField("grade", required=False, default="X",
                         regex=r'^[A-Z]$'),
                messages=self.messages
            )
            def a(self, id: int, name: str, grade: str) -> typing.Tuple:
                return id, name, grade

        a = AService()

        # 普通传参
        self.assertEqual(a.a(6, "Sam", "A"), (6, "Sam", "A"))
        # 完全字典传参
        self.assertEqual(a.a(id=6, name="Sam", grade=None), (6, "Sam", "X"))
        # 混合传参
        self.assertEqual(a.a(10, "Jack", grade="B"), (10, "Jack", "B"))

        # 出错

        # 不需要渲染msg的情况
        rs = a.a(None, "Sam", None)
        self.assertEqual(rs.status_code, 400)
        self.assertEqual(rs.reason, "id_empty")
        self.assertEqual(rs.msg, "id参数不能为空")

        # 需要渲染msg的情况
        rs = a.a(1, "Jack", None)
        self.assertEqual(rs.status_code, 400)
        self.assertEqual(rs.reason, "id_less_than_min")
        self.assertEqual(rs.msg, "id参数不能小于6")

    def testBadReq(self):
        """测试BadReq异常
        """

        class BService:

            @check(
                IntField("id"),
                messages=self.messages
            )
            def b(self, id):
                if id < 1:
                    raise BadReq("invalid_id", id=id)

        b = BService()
        rs = b.b(0)
        self.assertEqual(rs.status_code, 400)
        self.assertEqual(rs.reason, "invalid_id")
        self.assertEqual(rs.msg, "不合法的ID值'0'")
