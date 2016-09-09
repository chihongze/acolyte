import datetime
from abc import (
    ABCMeta,
    abstractmethod
)


class AbstractJob(metaclass=ABCMeta):

    """描述一个Job
       实现的其它Job均需要继承该类
    """

    def __init__(self, name, description, job_args=None):
        """
        :param name: Job名称
        :param description: Job描述
        :param job_args: Job参数声明
        """
        self._name = name
        self._description = description
        self._job_args = job_args if job_args is not None else {}

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def job_args(self):
        return self._job_args

    @abstractmethod
    def on_trigger(self, context, arguments):
        """当工作单元被触发时执行此动作
        """
        pass

    @abstractmethod
    def on_finish(self, context, arguments):
        """当工作单元结束时执行此动作
        """
        pass

    @abstractmethod
    def on_stop(self, context, arguments):
        """当工作单元被终止时执行此动作
        """
        pass

    @abstractmethod
    def on_exception(self, context, exc_type, exc_val, tb):
        """当Job执行出现异常时，执行此动作
        """
        pass


class JobStatus:

    """Job实例的各种运行状态
    """

    STATUS_WAITING = "waiting"

    STATUS_RUNNING = "running"

    STATUS_FINISHED = "finished"

    STATUS_STOPPED = "stopped"

    STATUS_EXCEPTION = "exception"


class JobInstance:

    """描述一个Job的运行状态
    """

    def __init__(self, id_, flow_instance_id, status,
                 trigger_actor, created_on=None, updated_on=None):
        """
        :param id_: 每个Job的运行实例有一个编号
        :param flow_instance_id: 隶属的flow_instance
        :param status: 运行状态
        :param trigger_actor: 触发者
        :param created_on: 运行实例起始时间
        :param updated_on: 最近更新状态时间
        """
        self.id = id_
        self.flow_instance_id = flow_instance_id
        self.status = status
        self.trigger_actor = trigger_actor
        if created_on is None:
            self.created_on = datetime.datetime.now()
        else:
            self.created_on = created_on

        if updated_on is None:
            self.updated_on = (self.created_on
                               if created_on is not None
                               else datetime.datetime.now())
        else:
            self.updated_on = updated_on


class JobActionData:

    """记录Job每一个Action执行的数据
    """

    def __init__(self, id_, job_instance_id, action, actor,
                 arguments, data, created_on=None, finished_on=None):
        """
        :param id_: Action实例编号
        :param job_instance_id: 隶属的job instance
        :param action: 动作名称
        :param actor: 执行者
        :param arguments: 执行该Action时所使用的参数
        :param data: 该Action执行后回填的数据
        :param created_on: 执行时间
        :param finished_on: 执行结束时间
        """

        self.id = id_
        self.job_instance_id = job_instance_id
        self.action = action
        self.actor = actor
        self.arguments = arguments
        self.data = data

        if created_on is None:
            self.created_on = datetime.datetime.now()
        else:
            self.created_on = created_on

        self.finished_on = finished_on


class JobRef:

    """还对象用于在FlowMeta等声明中引用一个Job
    """

    def __init__(self, name, **bind_args):
        self._name = name
        self._bind_args = bind_args if bind_args is not None else {}

    @property
    def name(self):
        return self._name

    @property
    def bind_args(self):
        return self._bind_args


class JobArg:

    """参数声明
    """

    TYPE_INT = "int"

    TYPE_FLOAT = "float"

    TYPE_STRING = "string"

    TYPE_LIST = "list"

    TYPE_DICT = "dict"

    # value: (类型, 默认的value_of函数)
    _TYPES = {
        TYPE_INT: (int, int),
        TYPE_FLOAT: (float, float),
        TYPE_STRING: (str, str),
        TYPE_LIST: (list, None),
        TYPE_DICT: (dict, None)
    }

    def __init__(self, name, type_name, comment, required=True, default="",
                 value_of=None, check_logic=None):
        """
        :param name:参数名称
        :param type_name: 类型名称
        :param comment: 参数说明
        :param required: 是否必须
        :param default: 默认值
        :param value_of: 转换函数，如果传递的类型不一致，会试图通过该函数转换
        :param check_logic: 检查逻辑
        """
        self.name = name
        self.type_name = type_name
        self.comment = comment
        self.required = required
        self.default = default
        self.value_of = value_of
        self.check_logic = check_logic
