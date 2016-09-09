"""本模块包含跟flow相关的facade接口
"""

from easemob_flow.core.service import (
    AbstractService,
    ViewObject,
    Result
)


class JobArgView(ViewObject):

    @classmethod
    def from_job_arg(cls, job_arg):
        return cls(job_arg.name, job_arg.type_name, job_arg.comment)

    def __init__(self, name, type_name, comment):
        self.name = name
        self.type = type_name
        self.comment = comment


class JobSimpleView(ViewObject):

    @classmethod
    def from_job(cls, job):
        job_args = {event: [
            JobArgView.from_job_arg(arg)
            for arg in job.job_args[
                event]] for event in job.job_args}
        return cls(job.name, job.description, job_args)

    def __init__(self, name, description, job_args):
        """
        :param name: Job名称
        :param description: 描述
        """
        self.name = name
        self.description = description
        self.job_args = job_args


class FlowMetaView(ViewObject):

    @classmethod
    def from_flow_meta(cls, flow_meta, job_mgr):
        jobs = [
            JobSimpleView.from_job(
                job_mgr.get(job_ref.name)
            ) for job_ref in flow_meta.jobs
        ]
        return cls(flow_meta.name, flow_meta.description, jobs)

    def __init__(self, name, description, jobs):
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
        super().__init__(service_container)

    def _after_register(self):
        # 注入两个manager
        self._flow_meta_mgr = self.service("flow_meta_manager")
        self._job_mgr = self.service("job_manager")

    def get_all_flow_meta(self):
        """获得所有注册到容器的flow_meta信息
        """
        all_flow_meta = [
            FlowMetaView.from_flow_meta(meta, self._job_mgr)
            for meta in self._flow_meta_mgr.all()
        ]
        return Result.ok(data=all_flow_meta)

    def get_flow_meta_info(self, flow_meta_name):
        """获取单个的flow_meta详情
        """
        return None

    def create_flow_template(self, flow_meta, bind_args, creator):
        """创建flow_template
        """
        pass

    def get_all_flow_templates(self):
        """获取所有的flow_templates列表
        """
        pass

    def get_flow_template(self, flow_template_id):
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
