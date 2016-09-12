from easemob_flow.util.service_container import ServiceContainer
from easemob_flow.core.service import (
    AbstractService,
    Result,
)
from easemob_flow.core.storage.flow_template import (
    FlowTemplateDAO,
)
from easemob_flow.core.storage.flow_instance import (
    FlowInstanceDAO,
)
from easemob_flow.util.validate import (
    IntField,
    StrField,
    Field,
    check,
    BadReq
)


class FlowExecutorService(AbstractService):

    def __init__(self, service_container: ServiceContainer):
        super().__init__("flow_executor_service", service_container)

    def _after_register(self):
        # 获取各种所依赖的服务
        self._db = self._("db")
        self._flow_tpl_dao = FlowTemplateDAO(self._db)
        self._flow_meta_mgr = self._("flow_meta_manager")
        self._job_mgr = self._("job_manager")
        self._flow_instance_dao = FlowInstanceDAO(self._db)

    @check(
        IntField("flow_template_id", required=True),
        IntField("initiator", required=True),
        StrField("description", required=True, max_len=20),
        Field("start_flow_args", type_=dict, required=False, default=None),
        Field("first_job_trigger_args", type_=dict,
              required=False, default=None)
    )
    def start_flow(self, flow_template_id: int, initiator: int,
                   description: str, start_flow_args: dict,
                   first_job_trigger_args: dict) -> Result:
        """开启一个flow进程，创建flow_instance并执行第一个Job

           S1. 根据flow_template_id获取flow_template，然后获取flow_meta，如果获取失败，返回错误
           S2. 检查并合并参数
           S3. 检查max_run_instance
           S4. 创建一条新的flow_instance记录
           S5. 创建context
           S6. 回调flow meta中on_start方法的逻辑
           S7. 回调第一个Job的trigger事件

           :param flow_template_id: 使用的flow template
           :param initiator: 发起人
           :param description: 本次flow描述
           :param start_flow_args: 执行FlowMeta的on_start方法时所需要的参数
           :param first_job_trigger_args: 执行第一个Job的trigger事件时所需要的参数
        """

        # 检查flow_template_id是否合法
        flow_template = self._flow_tpl_dao.query_flow_template_by_id(
            flow_template_id)
        if flow_template is None:
            raise BadReq("invalid_flow_template",
                         flow_template_id=flow_template_id)
        flow_meta = self._flow_meta_mgr.get(flow_template.flow_meta)
        if flow_meta is None:
            raise BadReq("invalid_flow_meta", flow_meta=flow_meta)

        # 检查并合并start_flow_args

        # 检查并合并first_job_trigger_args

    def next_job(self, flow_instance_id: int, current_job_finish_args: dict,
                 new_job_trigger_args: dict) -> Result:
        """执行下一个Job
           :param flow_instance_id: flow的标识，可以是flow_template或者flow_instance_id
           :param current_job_finish_args: 用于结束当前Job的参数
           :param new_job_trigger_args: 用于触发新Job的参数
           :return job_instance
        """
        pass

    def handle_job_action(self, flow_instance_id: int, job_action: str,
                          action_args: dict) -> Result:
        """处理Job中的自定义动作
           :param flow_instance_id: flow的标识
           :param job_action: 自定义的动作名称
           :param action_args: 执行该自定义动作所需要的参数
        """
        pass

    def stop(self, flow_instance_id: int, stop_flow_args: dict,
             stop_job_args: dict) -> Result:
        """终止flow
           :param flow_instance_id flow的标识
           :param stop_args 终止参数
        """
        pass
