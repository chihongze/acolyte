"""本模块包含跟flow相关的facade接口
"""

from easemob_flow.core.model import Result
from easemob_flow.core.mgr import (
    flow_meta_manager,
    job_manager
)


class JobSimpleView:

    @classmethod
    def from_job(cls, job):
        return cls(job.name, job.description)

    def __init__(self, name, description):
        """
        :param name: Job名称
        :param description: 描述
        """
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description


class FlowMetaView:

    @classmethod
    def from_flow_meta(cls, flow_meta):
        jobs = [
            JobSimpleView.from_job(
                job_manager.get(job_name)
            ) for job_name in flow_meta.jobs
        ]
        return cls(flow_meta.name, flow_meta.description, jobs)

    def __init__(self, name, description, jobs):
        """
        :param name: flow meta名称
        :param description: 描述
        :param jobs: job列表
        """
        self._name = name
        self._description = description
        self._jobs = jobs

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description


def get_all_flow_meta():
    """获得所有的flow_meta信息
    """
    all_flow_meta = [{} for meta in flow_meta_manager.all()]
    return Result.ok(data=all_flow_meta)


def get_flow_meta_info(flow_meta):
    """获取单个的flow_meta详情
    """
    return None


def create_flow_template(flow_meta, bind_args, creator):
    """创建flow_template
    """
    pass


def get_all_flow_templates():
    """获取所有的flow_templates列表
    """
    pass


def get_flow_template(flow_template_id):
    """获取单个的flow_template详情
    """
    pass


def get_flow_instance_by_status(status, offsert_id, limit, order):
    """根据当前的状态获取flow instance列表
    """
    pass


def get_flow_instance_by_template(template_id, offet_id, limit, order):
    """依据flow_template来查询flow实例
    """
    pass


def get_flow_instance_by_template_and_status(template_id, status,
                                             offset_id, limit, order):
    """依据flow_template和status来查询flow实例
    """
    pass


def get_flow_instance(flow_instance_id):
    """根据id获取flow实例
    """
    pass
