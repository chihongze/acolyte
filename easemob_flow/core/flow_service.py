"""本模块包含跟flow相关的facade接口
"""

import simplejson as json
import datetime
from easemob_flow.core.service import (
    AbstractService,
    ViewObject,
    Result
)
from easemob_flow.core.flow import FlowMeta
from easemob_flow.core.job import AbstractJob, JobArg
from easemob_flow.core.mgr import ObjectNotFoundException, AbstractManager
from easemob_flow.core.storage.flow_template import FlowTemplateDAO
from easemob_flow.core.storage.user import UserDAO


class JobArgView(ViewObject):

    @classmethod
    def from_job_arg(cls, job_arg: JobArg) -> ViewObject:
        return cls(job_arg.name, job_arg.type_name, job_arg.comment)

    def __init__(self, name: str, type_name: str, comment: str):
        self.name = name
        self.type = type_name
        self.comment = comment


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


class FlowService(AbstractService):

    def __init__(self, service_container):
        super().__init__("flow_service", service_container)

    def _after_register(self):
        # 注入两个manager
        self._flow_meta_mgr = self.service("flow_meta_manager")
        self._job_mgr = self.service("job_manager")
        db = self.service("db")
        self._flow_tpl_dao = FlowTemplateDAO(db)
        self._user_dao = UserDAO(db)

    def get_all_flow_meta(self) -> Result:
        """获得所有注册到容器的flow_meta信息
        """
        all_flow_meta = [
            FlowMetaView.from_flow_meta(meta, self._job_mgr)
            for meta in self._flow_meta_mgr.all()
        ]
        return Result.ok(data=all_flow_meta)

    def get_flow_meta_info(self, flow_meta_name: str) -> Result:
        """获取单个的flow_meta详情
        """

        try:
            flow_meta = self._flow_meta_mgr.get(flow_meta_name)
        except ObjectNotFoundException:
            return Result.bad_request(
                "flow_meta_not_exist",
                msg=self.msg("get_flow_meta_info", "flow_meta_not_exist",
                             flow_meta=flow_meta_name))

        return Result.ok(data=FlowMetaView.from_flow_meta(
            flow_meta, self._job_mgr))

    def create_flow_template(self, flow_meta: str, name: str, bind_args: dict,
                             max_run_instance: int, creator: int) -> Result:
        """创建flow_template
        """

        _mtd = "create_flow_template"

        # 检查max_run_instance
        if max_run_instance < 0:
            return Result.bad_request(_mtd, "invalid_max_run_instance",
                                      max_run_instance=max_run_instance)

        # 获取flow_meta以及检查其存在性
        try:
            self._flow_meta_mgr.get(flow_meta)
        except ObjectNotFoundException:
            return Result.bad_request(_mtd, "flow_meta_not_exist",
                                      flow_meta=flow_meta)

        # 检查name是否已经存在
        if self._flow_tpl_dao.is_name_existed(name):
            return Result.bad_reques(_mtd, "name_already_exist", name=name)

        # 检查creator是否存在
        if not self._user_dao.is_name_existed(creator):
            return Result.bad_request(_mtd, "invalid_creator_id",
                                      creator=creator)

        created_on = datetime.datetime.now()

        # 插入吧!
        self._flow_tpl_dao.insert_flow_template(
            flow_meta, name, json.dumps(bind_args),
            max_run_instance, creator, created_on)

    def get_all_flow_templates(self):
        """获取所有的flow_templates列表
        """
        pass

    def get_flow_template(self, flow_template_id: int):
        """获取单个的flow_template详情
        """
        pass

    def get_flow_instance_by_status(self, status, offsert_id, limit, order):
        """根据当前的状态获取flow instance列表
        """
        pass

    def get_flow_instance_by_template(self, template_id,
                                      offet_id, limit, order):
        """依据flow_template来查询flow实例
        """
        pass

    def get_flow_instance_by_template_and_status(self, template_id, status,
                                                 offset_id, limit, order):
        """依据flow_template和status来查询flow实例
        """
        pass

    def get_flow_instance(self, flow_instance_id):
        """根据id获取flow实例
        """
        pass
