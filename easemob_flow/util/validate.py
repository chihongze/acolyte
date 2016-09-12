import re
import locale
from functools import wraps
from typing import Any
from types import FunctionType
from easemob_flow.exception import EasemobFlowException
from easemob_flow.core.message import (
    messages,
    default_validate_messages
)
from easemob_flow.core.service import Result
from easemob_flow.util.lang import get_from_nested_dict


class Field:

    """该类型对象用于描述一个字段的类型、转换规则、验证逻辑等等
    """

    def __init__(self, name: str, type_: type, required: bool=True,
                 default: Any=None,
                 value_of: type or FunctionType or None=None,
                 check_logic: FunctionType or None=None):
        """
        :param name: 字段名称
        :param type_: 期待类型
        :param required: 该字段是否是必须的
        :param default: 如果不是必须的，该字段的默认值
        :param value_of: 如果类型不匹配，回调该函数进行转换
        :param check_logic: 验证逻辑
        """
        self._name = name
        self._type = type_
        self._required = required
        self._default = default
        self._value_of = value_of
        self._check_logic = check_logic

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def required(self):
        return self._required

    @property
    def default(self):
        return self._default

    def __call__(self, value: Any) -> Any:
        """调用call完成对目标值的转换和检查
        """

        value = self._base_check(value)

        value = self._customize_check(value)

        # 检查逻辑
        if self._check_logic is not None:
            _result = self._check_logic(self._name, value)
            if _result is not None:
                value = _result

        # 返回最终转换的结果
        return value

    def _base_check(self, value: Any) -> Any:
        # 必须且为空，抛出异常
        if self._required and value is None:
            raise InvalidFieldException(self._name, value, "empty", "")

        # 非必须且为空，返回默认值
        if not self._required and value is None:
            return self._default

        # 类型与期望不符，
        if not isinstance(value, self._type):
            if self._value_of is not None:
                try:
                    value = self._value_of(value)
                except Exception:
                    raise InvalidFieldException(
                        self._name, value, "invalid_type", self._type)
            else:
                raise InvalidFieldException(
                    self._name, value, "invalid_type", self._type)

        return value

    def _customize_check(self, value):
        """自定义检查，子类可以实现
        """
        return value


class IntField(Field):

    """该类型对象用于描述一个整数值的验证规则
    """

    def __init__(self, name: str, required: bool=True,
                 default: int=0, value_of: type or FunctionType or None=int,
                 min_: int or None=None, max_: int or None=None,
                 check_logic: FunctionType or None=None):
        """
        :param min: 最小值
        :param max: 最大值
        """
        super().__init__(
            name=name,
            type_=int,
            required=required,
            default=default,
            value_of=value_of,
            check_logic=check_logic
        )

        self._min, self._max = min_, max_

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    def _customize_check(self, value):

        # 比最小值还要小
        if self._min is not None and value < self._min:
            raise InvalidFieldException(
                self._name, value, "less_than_min", self._min)

        # 比最大值还大
        if self._max is not None and value > self._max:
            raise InvalidFieldException(
                self._name, value, "more_than_max", self._max)

        return value


class StrField(Field):

    """该类型对象用于描述一个字符串值的验证规则
    """

    def __init__(self, name: str, required: bool=True,
                 default: int=0, value_of: type or FunctionType or None=str,
                 min_len: int or None=None, max_len: int or None=None,
                 regex: str or None=None,
                 check_logic: FunctionType or None=None):
        """
        :param min_length: 允许的最小长度
        :param max_length: 允许的最大长度
        :param regex: 满足的正则表达式
        """
        super().__init__(
            name=name,
            type_=str,
            required=required,
            default=default,
            value_of=value_of,
            check_logic=check_logic
        )
        self._min_len, self._max_len = min_len, max_len
        self._regex = regex

    @property
    def min_len(self):
        return self._min_len

    @property
    def max_len(self):
        return self._max_len

    @property
    def regex(self):
        return self._regex

    def _customize_check(self, value):

        # 检查长度

        val_length = len(value)

        if self._min_len is not None and val_length < self._min_len:
            raise InvalidFieldException(
                self._name, value, "less_than_min_length", self._min_len)

        if self._max_len is not None and val_length > self._max_len:
            raise InvalidFieldException(
                self._name, value, "more_than_max_length", self._max_len)

        if self._regex is not None and not re.search(self._regex, value):
            raise InvalidFieldException(
                self._name, value, "invalid_format", self._regex)

        return value


class InvalidFieldException(EasemobFlowException):

    """当字段不满足Rule对象的期望条件时，抛出此异常
    """

    def __init__(self, field_name, value, reason, expect):
        """
        :param field_name: 字段名称
        :param value: 字段值
        :param reason: 引发错误原因
        :param expect: 期望的类型/值/规则
        """
        self._field_name = field_name
        self._value = value
        self._reason = reason
        self._expect = expect
        super().__init__((
            "Invalid field {field}={value}, "
            "reason={reason}, expect={expect}"
        ).format(field=field_name, value=value, reason=reason, expect=expect))

    @property
    def field_name(self):
        return self._field_name

    @property
    def value(self):
        return self._value

    @property
    def reason(self):
        return self._reason

    @property
    def expect(self):
        return self._expect


class BadReq(Exception):

    """被check修饰的服务接口抛出此异常，可以直接返回bad request result
    """

    def __init__(self, reason, **args):
        self._reason = reason
        self._args = args

    @property
    def reason(self):
        return self._reason

    @property
    def args(self):
        return self._args


def check(*fields, messages=messages,
          default_validate_messages=default_validate_messages):
    """该decorator用在service对象方法上验证参数
       :param fields: 参数规则声明
       :pram messages: 消息集合
    """

    fields_dict = {f.name: f for f in fields}

    def _check(f):

        @wraps(f)
        def _func(self, *args, **kwds):
            nonlocal fields_dict

            try:
                # 组装并验证参数
                new_args = [field(arg_val)
                            for field, arg_val in zip(fields, args)]
                new_kwds = {arg_name: fields_dict[arg_name](arg_val)
                            for arg_name, arg_val in kwds.items()}
            except InvalidFieldException as e:
                full_reason = "{field_name}_{reason}".format(
                    field_name=e.field_name, reason=e.reason)
                loc, _ = locale.getlocale(locale.LC_ALL)
                service_id = self.__class__.__name__
                mtd_name = f.__name__

                # 先从用户messages集合中获取
                msg = get_from_nested_dict(
                    messages, loc, service_id, mtd_name, full_reason)
                if msg is None:
                    # 用户messages集合取不到再取默认的
                    msg = default_validate_messages[loc][e.reason]
                    if e.expect is not None or e.expect != "":
                        msg = msg.format(
                            field_name=e.field_name, expect=e.expect)
                    else:
                        msg = msg.format(field_name=e.field_name)
                else:
                    if e.expect is not None or e.expect != "":
                        msg = msg.format(expect=e.expect)

                return Result.bad_request(full_reason, msg=msg)
            else:
                try:
                    return f(self, *new_args, **new_kwds)
                except BadReq as e:
                    loc, _ = locale.getlocale(locale.LC_ALL)
                    msg = messages[loc][
                        self.__class__.__name__][f.__name__][e.reason]
                    if e.args:
                        msg = msg.format(**e.args)

                    return Result.bad_request(e.reason, msg=msg)

        return _func

    return _check


def declare_args(*fields):
    """该decorator用于在方法上声明验证规则
       被修饰的方法对象会拥有一个field_rules对象
       :param fields: 被修饰函数的参数规则集合
    """

    def _declare_args(f):

        f.field_rules = fields

        @wraps(f)
        def _func(*args, **kwds):
            return f(*args, **kwds)

        return _func

    return _declare_args
