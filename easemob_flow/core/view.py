from abc import ABCMeta
from easemob_flow.core.job import AbstractJob, JobArg
from easemob_flow.core.flow import FlowMeta
from easemob_flow.core.mgr import AbstractManager


class ViewObject(metaclass=ABCMeta):

    """ViewObject用做最终输出的视图对象，可以直接序列化为json
    """
    pass


class FlowMetaView(ViewObject):

    @classmethod
    def from_flow_meta(cls, flow_meta: FlowMeta, job_mgr: AbstractManager):
        jobs = [
            JobSimpleView.from_job(
                job_mgr.get(job_ref.name)
            ) for job_ref in flow_meta.jobs
        ]
        return cls(flow_meta.name, flow_meta.description, jobs)

    def __init__(self, name: str, description: str, jobs: list):
        """
        :param name: flow meta名称
        :param description: 描述
        :param jobs: job列表
        """
        self.name = name
        self.description = description
        self.jobs = jobs


class JobSimpleView(ViewObject):

    @classmethod
    def from_job(cls, job: AbstractJob) -> ViewObject:
        job_args = {event: [
            JobArgView.from_job_arg(arg)
            for arg in job.job_args[
                event]] for event in job.job_args}
        return cls(job.name, job.description, job_args)

    def __init__(self, name: str, description: str, job_args: dict):
        """
        :param name: Job名称
        :param description: 描述
        """
        self.name = name
        self.description = description
        self.job_args = job_args


class JobArgView(ViewObject):

    @classmethod
    def from_job_arg(cls, job_arg: JobArg) -> ViewObject:
        return cls(job_arg.name, job_arg.type_name, job_arg.comment)

    def __init__(self, name: str, type_name: str, comment: str):
        self.name = name
        self.type = type_name
        self.comment = comment
