import datetime
from abc import ABCMeta, abstractmethod


class FlowMeta(metaclass=ABCMeta):

    """flow meta
       每个流程都可以抽象成flow meta，比如工程更新、SQL审核、机器审核等等
    """

    def __init__(self, name: str, jobs: list, start_args: dict=None,
                 stop_args: dict=None, description: str=""):
        """
        :param name: flow meta名称
        :param jobs: 包含的JobRef对象列表
        :param bind_args: 绑定的静态参数，格式 {start: {args}, stop: {args}}
        """
        self._name = name
        self._jobs = jobs
        self._start_args = start_args
        self._stop_args = stop_args
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def jobs(self):
        return self._jobs

    @property
    def start_args(self):
        if self._start_args is None:
            return {}
        return self._start_args

    @property
    def stop_args(self):
        if self._stop_args is None:
            return {}
        return self._stop_args

    @property
    def description(self):
        return self._description

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

    @abstractmethod
    def on_exception(self, context, exc_type, exc_value, tb):
        """当发生异常时，执行此逻辑
        """
        pass


class FlowTemplate:

    def __init__(self, id_: int, flow_meta: str, name: str, bind_args: dict,
                 max_run_instance: int, creator: int,
                 created_on: datetime.datetime):
        """根据FlowMeta来生成的Flow模板
           :param flow_meta: 使用的flow_meta
           :param name: 模板名称
           :param bind_args: 绑定的参数
           :param max_run_instance: 最大可运行实例数目
           :param creator: 创建者
           :param created_on: 创建时间
        """
        self.id = id_
        self.flow_meta = flow_meta
        self.name = name
        self.bind_args = bind_args
        self.max_run_instance = max_run_instance
        self.creator = creator
        self.created_on = created_on


class FlowStatus:

    """flow的当前运行状态
    """

    STATUS_WAITING = "waiting"  # 等待执行

    STATUS_RUNNING = "running"  # 正在执行

    STATUS_FINISHED = "finished"  # 已经完成

    STATUS_STOPPED = "stopped"  # 已经终止

    STATUS_EXCEPTION = "exception"  # 由于异常而终止


class FlowInstance:

    """描述flow template的运行实例
    """

    def __init__(self, id_: int, flow_template_id: int, initiator: int,
                 current_step: str=None, status: str=FlowStatus.STATUS_WAITING,
                 description: str=None, created_on: datetime.datetime=None,
                 updated_on: datetime.datetime=None):
        """
        :param id_: 每个flow运行实例都会有一个唯一ID
        :param flow_template_id: 所属的flow_template
        :param initiator: 发起人
        :param current_step: 当前执行到的步骤
        :param status: 执行状态
        :param created_on: 创建时间
        :param updated_on: 最新更新步骤时间
        """

        self.id = id_
        self.flow_template_id = flow_template_id
        self.initiator = initiator
        self.current_step = current_step
        self.status = status
        self.description = description

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
