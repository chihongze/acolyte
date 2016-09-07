import ujson
import datetime
from abc import ABCMeta, abstractmethod
from easemob_flow.util.lang import to_str


class FlowMeta(meta=ABCMeta):

    """flow meta
       每个流程都可以抽象成flow meta，比如工程更新、SQL审核、机器审核等等
    """

    def __init__(self, name, jobs, bind_args):
        """
        :param name: flow meta名称
        :param jobs: 包含的Job列表
        :param bind_args: 绑定的静态参数，格式 {jobA: {args}, jobB: {args}}
        """
        self._name = name
        self._jobs = jobs
        self._bind_args = bind_args

    @property
    def name(self):
        return self._name

    @property
    def jobs(self):
        return self._jobs

    @property
    def bind_args(self):
        return self._bind_args

    @abstractmethod
    def on_start(self, context, arguments):
        """当Flow启动时，执行此逻辑
           :param context: flow执行上下文
           :param arguments: 生成的运行时参数
        """
        pass

    @abstractmethod
    def on_stop(self, context, arguments):
        """当Flow被终止时，执行此逻辑
           :param context: flow执行上下文
           :param arguments: 生成的运行时参数
        """
        pass

    @abstractmethod
    def on_finish(self, context):
        """当flow结束是，执行此逻辑
           :param context: flow执行上下文
        """
        pass

    def __repr__(self):
        return to_str(self, "name",
                      ("jobs", lambda jobs: [j.name for j in jobs]),
                      ("bind_args", ujson.dumps),
                      "max_run_instance")

    def __str__(self):
        return self.__repr__()


class FlowTemplate:

    def __init__(self, id_, flow_meta, name, bind_args, max_run_instance,
                 creator, created_on):
        """根据FlowMeta来生成的Flow模板
           :param flow_meta: 使用的flow_meta
           :param name: 模板名称
           :param bind_args: 绑定的参数
           :param max_run_instance: 最大可运行实例数目
           :param creator: 创建者
           :param created_on: 创建时间
        """
        self._id = id_
        self._flow_meta = flow_meta
        self._name = name
        self._bind_args = bind_args
        self._max_run_instance = max_run_instance
        self._creator = creator
        self._created_on = created_on

    @property
    def id(self):
        return self._id

    @property
    def flow_meta(self):
        return self._flow_meta

    @property
    def name(self):
        return self._name

    @property
    def bind_args(self):
        return self._bind_args

    @property
    def max_run_instance(self):
        return self._max_run_instance

    @property
    def creator(self):
        return self._creator

    @property
    def created_on(self):
        return self._created_on


class FlowStatus:

    """flow的当前运行状态
    """

    STATUS_WAITING = "waiting"  # 等待执行

    STATUS_RUNNING = "running"  # 正在执行

    STATUS_FINISHED = "finished"  # 已经完成

    STATUS_STOPPED = "stopped"  # 已经终止


class FlowRunInstance:

    """描述flow template的运行实例
    """

    def __init__(self, id_, flow_template, initiator,
                 current_step=None, status=FlowStatus.STATUS_WAITING,
                 description=None, created_on=None, updated_on=None):
        """
        :param id_: 每个flow运行实例都会有一个唯一ID
        :param flow_template_id: 所属的flow_template
        :param initiator: 发起人
        :param current_step: 当前执行到的步骤
        :param status: 执行状态
        :param created_on: 创建时间
        :param updated_on: 最新更新步骤时间
        """

        self._id = id_
        self._flow_template = flow_template
        self._initiator = initiator
        self._current_step = current_step
        self._status = status
        self._description = description

        if created_on is None:
            self._created_on = datetime.datetime.now()
        else:
            self._created_on = created_on

        if updated_on is None:
            self._updated_on = (self._created_on
                                if created_on is not None
                                else datetime.datetime.now())
        else:
            self._updated_on = updated_on

    @property
    def id(self):
        return self._id

    @property
    def flow_template(self):
        return self._flow_template

    @property
    def mark(self):
        return self._mark

    @property
    def initiator(self):
        return self._initiator

    @property
    def current_step(self):
        return self._current_step

    @property
    def status(self):
        return self._status

    @property
    def created_on(self):
        return self._created_on

    @property
    def updated_on(self):
        return self._updated_on

    @property
    def description(self):
        return self._description
