import typing
from abc import ABCMeta
from easemob_flow.core.job import AbstractJob, JobArg
from easemob_flow.core.flow import FlowMeta
from easemob_flow.core.mgr import AbstractManager
from easemob_flow.util.validate import (
    Field,
    IntField,
    StrField
)


class ViewObject(metaclass=ABCMeta):

    """ViewObject用做最终输出的视图对象，可以直接序列化为json
    """
    pass


class FlowMetaView(ViewObject):

    """FlowMeta渲染视图
    """

    @classmethod
    def from_flow_meta(cls, flow_meta: FlowMeta, job_mgr: AbstractManager):
        """从FlowMeta对象来构建
           :param flow_meta: flow meta对象
           :param job_mgr: 用于获取Job对象
        """
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
        :param job_args: Job的参数声明
        """
        self.name = name
        self.description = description
        self.job_args = job_args


class FieldInfoView(ViewObject):

    """字段的类型和验证视图
    """

    @classmethod
    def from_field_obj(cls, field: Field):
        """从Field对象进行构建
        """
        if isinstance(field, StrField):
            return _StrFieldView(field.required, field.default,
                                 field.min_len, field.max_len, field.regex)
        elif isinstance(field, IntField):
            return _IntFieldView(
                field.required, field.default, field.min, field.max)
        else:
            return cls(field.type.__name__, field.required, field.default)

    def __init__(self, type_: str, required: bool, default: typing.Any):
        self.type = type_
        self.required = required
        self.default = default


class _IntFieldView(FieldInfoView):

    def __init__(self, required: bool, default: int,
                 min_: int or None, max_: int or None):
        super().__init__('int', required, default)
        self.min = min_
        self.max = max_


class _StrFieldView(FieldInfoView):

    def __init__(self, required: bool, default: str,
                 min_len: int or None, max_len: int or None,
                 regex: str or None):
        super().__init__('str', required, default)
        self.min_len = min_len
        self.max_len = max_len
        self.regex = regex


class JobArgView(ViewObject):

    @classmethod
    def from_job_arg(cls, job_arg: JobArg) -> ViewObject:
        return cls(
            job_arg.name,
            FieldInfoView.from_field_obj(job_arg.field_info),
            job_arg.mark,
            job_arg.comment,
        )

    def __init__(self, name: str, field_info: FieldInfoView,
                 mark: str, comment: str):
        self.name = name
        self.field_info = field_info
        self.mark = mark
        self.comment = comment
