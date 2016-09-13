import locale
import simplejson as json
from collections import ChainMap
from typing import Dict, Any
from acolyte.util.service_container import ServiceContainer
from acolyte.core.service import (
    AbstractService,
    Result,
)
from acolyte.core.context import MySQLContext
from acolyte.core.storage.user import UserDAO
from acolyte.core.storage.flow_template import (
    FlowTemplateDAO,
)
from acolyte.core.storage.flow_instance import (
    FlowInstanceDAO,
)
from acolyte.core.message import default_validate_messages
from acolyte.util.validate import (
    IntField,
    StrField,
    Field,
    check,
    BadReq,
    InvalidFieldException
)


class FlowExecutorService(AbstractService):

    def __init__(self, service_container: ServiceContainer):
        super().__init__(service_container)

    def _after_register(self):
        # 获取各种所依赖的服务
        self._db = self._("db")
        self._flow_tpl_dao = FlowTemplateDAO(self._db)
        self._flow_meta_mgr = self._("flow_meta_manager")
        self._job_mgr = self._("job_manager")
        self._flow_instance_dao = FlowInstanceDAO(self._db)
        self._user_dao = UserDAO(self._db)

    @check(
        IntField("flow_template_id", required=True),
        IntField("initiator", required=True),
        StrField("description", required=True, max_len=20),
        Field("start_flow_args", type_=dict, required=False,
              default=None, value_of=json.loads),
    )
    def start_flow(self, flow_template_id: int,
                   initiator: int, description: str,
                   start_flow_args: Dict[str, Any]) -> Result:
        """开启一个flow进程，创建flow_instance并执行第一个Job

           S1. 根据flow_template_id获取flow_template，然后获取flow_meta，如果获取失败，返回错误
           S2. 检查并合并参数
           S3. 检查max_run_instance
           S4. 创建一条新的flow_instance记录
           S5. 创建context
           S6. 回调flow meta中on_start方法的逻辑

           :param flow_template_id: 使用的flow template
           :param initiator: 发起人
           :param description: 本次flow描述
           :param start_flow_args: 执行FlowMeta的on_start方法时所需要的参数
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

        # 检查发起者
        initiator_user = self._user_dao.query_user_by_id(initiator)
        if initiator_user is None:
            raise BadReq("invalid_initiator", initiator=initiator)

        # 检查并合并start_flow_args
        field_rules = getattr(flow_meta.on_start, "field_rules")
        rs = self._combine_and_check_args(
            "start", field_rules, start_flow_args, flow_meta.start_args)
        if rs.status_code == Result.STATUS_BADREQUEST:
            return rs
        start_flow_args = rs.data

        # 锁定检查instance数目并创建第一条记录
        flow_instance = None
        if flow_template.max_run_instance > 0:
            lock_key = "lock_instance_create_{tpl_id}".format(
                tpl_id=flow_template_id)
            with self._db.lock(lock_key):
                current_instance_num = self._flow_instance_dao.\
                    query_instance_num_by_tpl_id(flow_template_id)
                if current_instance_num >= flow_template.max_run_instance:
                    raise BadReq(
                        reason="too_many_instance",
                        allow_instance_num=flow_template.max_run_instance
                    )
                flow_instance = self._flow_instance_dao.insert(
                    flow_template_id, initiator, description)
        else:
            flow_instance = self._flow_instance_dao.insert(
                flow_template_id, initiator, description)

        # 创建Context
        ctx = MySQLContext(self, self._db, flow_instance.id)

        # 回调on_start
        flow_meta.on_start(ctx, *start_flow_args)
        return Result.ok(data=flow_instance)

    def handle_job_action(self, flow_instance_id: int, job_action: str,
                          action_args: Dict[str, Any]) -> Result:
        """处理Job中的自定义动作
           :param flow_instance_id: flow的标识
           :param job_action: 自定义的动作名称
           :param action_args: 执行该自定义动作所需要的参数
        """
        pass

    def _combine_and_check_args(self, action_name, field_rules, *args_dict):
        """合并 & 检查参数 先合并，后检查
           :param field_rules: 字段规则
           :param old_args
        """
        _combined_args = ChainMap(*args_dict).new_child()

        # 木有验证规则，直接返回数据
        if not field_rules:
            return Result.ok(data=_combined_args)

        try:
            for field_rule in field_rules:
                # 检查并替换掉相关参数
                val = field_rule(_combined_args[field_rule.name])
                _combined_args[field_rule.name] = val
        except InvalidFieldException as e:
            loc, _ = locale.getlocale(locale.LC_ALL)
            full_field_name = "{action_name}.{field_name}".format(
                action_name=action_name,
                field_name=e.field_name
            )
            full_reason = "{full_field_name}_{reason}".format(
                full_field_name=full_field_name,
                reason=e.reason
            )
            msg = default_validate_messages[loc][e.reason]
            if e.expect is None or e.expect == "":
                msg = msg.format(field_name=full_field_name)
            else:
                msg = msg.format(
                    field_name=full_field_name, expect=e.expect)
            return Result.bad_request(reason=full_reason, msg=msg)
        else:
            return Result.ok(data=_combined_args)
