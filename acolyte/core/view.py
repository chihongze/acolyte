import typing
from abc import ABCMeta
from acolyte.core.job import JobArg
from acolyte.core.flow import FlowMeta
from acolyte.core.mgr import AbstractManager
from acolyte.util.validate import (
    Field,
    IntField,
    StrField
)


class ViewObject(metaclass=ABCMeta):

    """ViewObject用做最终输出的视图对象，可以直接序列化为json
    """
    pass


class UserSimpleView(ViewObject):

    """用户信息的简单视图
    """

    @classmethod
    def from_user(cls, user):
        return cls(user.id, user.email, user.name)

    def __init__(self, id_, email, name):
        self.id = id_
        self.email = email
        self.name = name


class FlowMetaView(ViewObject):

    """FlowMeta渲染视图
    """

    @classmethod
    def from_flow_meta(cls, flow_meta: FlowMeta, job_mgr: AbstractManager):
        """从FlowMeta对象来构建
           :param flow_meta: flow meta对象
           :param job_mgr: 用于获取Job对象
        """
        jobs = [JobRefView.from_job_ref(job_ref) for job_ref in flow_meta.jobs]
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


class JobRefView(ViewObject):

    @classmethod
    def from_job_ref(cls, job_ref) -> ViewObject:
        return cls(job_ref.step_name, job_ref.job_name, job_ref.bind_args)

    def __init__(self, step_name: str, job_name: str,
                 bind_args: dict):
        """
        :param step_name: 步骤名称
        :param job_name: Job名称
        :param bind_args: 绑定参数
        """
        self.step_name = step_name
        self.job_name = job_name
        self.bind_args = bind_args


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


class FlowTemplateView(ViewObject):

    @classmethod
    def from_flow_template(cls, flow_template, user):
        return FlowTemplateView(
            id_=flow_template.id,
            flow_meta=flow_template.flow_meta,
            name=flow_template.name,
            bind_args=flow_template.bind_args,
            max_run_instance=flow_template.max_run_instance,
            creator_info=UserSimpleView.from_user(user)
        )

    def __init__(self, id_: int, flow_meta: str, name: str,
                 bind_args: dict, max_run_instance: int,
                 creator_info: UserSimpleView):
        self.id = id_
        self.flow_meta = flow_meta
        self.name = name
        self.bind_args = bind_args
        self.max_run_instance = max_run_instance
        self.creator_info = creator_info


class FlowTemplateSimpleView(ViewObject):

    """简化版的FlowTemplate视图
       主要用于FlowInstance视图
    """

    @classmethod
    def from_flow_template(cls, flow_template, flow_meta_mgr):
        flow_meta = flow_meta_mgr.get(flow_template.flow_meta)
        return cls(flow_template.id, flow_meta.name, flow_template.name)

    def __init__(self, id_, flow_meta_name, name):
        """
        :param id_: 编号
        :param flow_meta_name: flow meta名称
        :param name: flow template名称
        """
        self.id = id_
        self.flow_meta_name = flow_meta_name
        self.name = name


class FlowSimpleInstanceView(ViewObject):

    """描述一个FlowInstance的简单实例
    """

    @classmethod
    def from_flow_instance(
            cls, flow_instance, flow_template, flow_meta_mgr, creator):

        return cls(
            id_=flow_instance.id,
            status=flow_instance.status,
            description=flow_instance.description,
            current_step=flow_instance.current_step,
            created_on=flow_instance.created_on,
            updated_on=flow_instance.updated_on,
            flow_template_info=FlowTemplateSimpleView.from_flow_template(
                flow_template, flow_meta_mgr),
            creator_info=UserSimpleView.from_user(creator)
        )

    def __init__(self, id_, status, description, current_step,
                 created_on, updated_on, flow_template_info, creator_info):
        """
        :param id_: 编号
        :param status: 状态
        :param description: 描述
        :param current_step: 当前运行到的步骤
        :param created_on: 创建时间
        :param updated_on: 最近更新时间
        :param flow_template_info: flow_template视图
        :param creator_info: creator视图
        """
        self.id = id_
        self.status = status
        self.description = description
        self.current_step = current_step
        self.created_on = created_on
        self.updated_on = updated_on
        self.flow_template_info = flow_template_info
        self.creator_info = creator_info
