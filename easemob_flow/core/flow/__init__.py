import ujson
import datetime
from abc import ABCMeta, abstractmethod
from easemob_flow.util.lang import to_str


class FlowTemplate:

    """flow模板
       每个流程都可以抽象成flow模板，比如工程更新、SQL审核、机器审核等等
    """

    def __init__(self, name, jobs, bind_args, max_run_instance=1):
        """
        :param name: flow模板名称
        :param jobs: 包含的Job列表
        :param bind_args: 绑定参数，格式 {jobA: {args}, jobB: [args]}
        :param max_run_instance: flow最多允许运行实例，默认为1，
                                 比如同一时刻，只允许某个人更新工程，
                                 如果为0则不限制，比如同一时刻允许多个人进行SQL审核
        """
        self._name = name
        self._jobs = jobs
        self._bind_args = bind_args
        self._max_run_instance = max_run_instance

    @property
    def name(self):
        return self._name

    @property
    def jobs(self):
        return self._jobs

    @property
    def bind_args(self):
        return self._bind_args

    @property
    def max_run_instance(self):
        return self._max_run_instance

    def __repr__(self):
        return to_str(self, "name",
                      ("jobs", lambda jobs: [j.name for j in jobs]),
                      ("bind_args", ujson.dumps),
                      "max_run_instance")

    def __str__(self):
        return self.__repr__()


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

    def __init__(self, id_, flow_template_id, mark, initiator,
                 current_step=None, status=FlowStatus.STATUS_WAITING,
                 created_on=None, updated_on=None):
        """
        :param id_: 每个flow运行实例都会有一个唯一ID
        :param flow_template_id: 所属的flow_template
        :param mark: 标记，用于描述此次流程，比如REST服务更新release-1.1.1
        :param initiator: 发起人
        :param current_step: 当前执行到的步骤
        :param status: 执行状态
        :param created_on: 创建时间
        :param updated_on: 最新更新步骤时间
        """

        self._id = id_
        self._flow_template_id = flow_template_id
        self._mark = mark
        self._initiator = initiator
        self._current_step = current_step
        self._status = status

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
    def flow_template_id(self):
        return self._flow_template_id

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


class AbstractFlowExecutor(meta=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def start_flow(self, flow_name, first_job_trigger_args):
        """开启一个flow进程，创建flow_instance并执行第一个Job
           :param flow_name: 具体的flow_template的名称
           :param first_job_trigger_args: 触发第一个Job需要的参数
           :return flow_instance
        """
        pass

    @abstractmethod
    def next_job(self, flow_instance_id, current_job_finish_args,
                 new_job_trigger_args):
        """执行下一个Job
           :param flow_instance_id: flow的标识，可以是flow_template或者flow_instance_id
           :param current_job_finish_args: 
           :return job_instance
        """
        pass

    @abstractmethod
    def stop(self, flow_instance_id, stop_args):
        """终止flow
           :param flow_instance_id flow的标识
        """
        pass
