import ujson
import datetime
from abc import (
    ABCMeta,
    abstractmethod
)
from easemob_flow.util.time import common_fmt_dt
from easemob_flow.util.lang import to_str


class AbstractJob(meta=ABCMeta):

    """描述一个Job
       实现的其它Job均需要继承该类
    """

    def __init__(self, name, description):
        """
        :param name: Job名称
        :param description: Job描述
        """
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @abstractmethod
    def on_trigger(self, *args, **kwds):
        """当工作单元被触发时执行此动作
        """
        pass

    @abstractmethod
    def on_finish(self, *args, **kwds):
        """当工作单元结束时执行此动作
        """
        pass

    @abstractmethod
    def on_stop(self, *args, **kwds):
        """当工作单元被终止时执行此动作
        """
        pass

    def __repr__(self):
        return to_str(self, "name", "description")

    def __str__(self):
        return self.__repr__()


class JobStatus:

    """Job实例的各种运行状态
    """

    STATUS_WAITING = "waiting"

    STATUS_RUNNING = "running"

    STATUS_FINISHED = "finished"

    STATUS_STOPPED = "stopped"


class JobRunInstance:

    """描述一个Job的运行状态
    """

    def __init__(self, id_, flow_instance_id, status, running_data,
                 created_on=None, updated_on=None):
        """
        :param id_: 每个Job的运行实例有一个编号
        :param flow_instance_id: 隶属的flow_instance
        :param status: 运行状态
        :param running_data: 运行数据
        :param created_on: 运行实例起始时间
        :param updated_on: 最近更新状态时间
        """
        self._id = id_
        self._flow_instance_id = flow_instance_id
        self._status = status
        self._running_data = running_data
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
    def flow_instance_id(self):
        return self._flow_instance_id

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def running_data(self):
        return self._running_data

    @running_data.setter
    def running_data(self, running_data):
        self._running_data = running_data

    @property
    def created_on(self):
        return self._created_on

    @property
    def updated_on(self):
        return self._updated_on

    @updated_on.setter
    def updated_on(self, updated_on):
        self._updated_on = updated_on

    def __repr__(self):
        return to_str(self,
                      "id", "flow_instance_id", "status",
                      ("running_data", ujson.dumps),
                      ("created_on", common_fmt_dt),
                      ("updated_on", common_fmt_dt))

    def __str__(self):
        return self.__repr__()
