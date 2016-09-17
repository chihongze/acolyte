import locale
import simplejson as json
from collections import ChainMap
from typing import Dict, Any
from acolyte.util.service_container import ServiceContainer
from acolyte.core.service import (
    AbstractService,
    Result,
)
from acolyte.core.flow import FlowStatus
from acolyte.core.job import JobStatus, JobArg
from acolyte.core.context import MySQLContext
from acolyte.core.storage.user import UserDAO
from acolyte.core.storage.flow_template import FlowTemplateDAO
from acolyte.core.storage.flow_instance import FlowInstanceDAO
from acolyte.core.storage.job_instance import JobInstanceDAO
from acolyte.core.storage.job_action_data import JobActionDataDAO
from acolyte.core.message import default_validate_messages
from acolyte.util.validate import (
    IntField,
    StrField,
    Field,
    check,
    BadReq,
    InvalidFieldException
)
from acolyte.exception import ObjectNotFoundException


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
        self._job_instance_dao = JobInstanceDAO(self._db)
        self._job_action_dao = JobActionDataDAO(self._db)

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

        if start_flow_args is None:
            start_flow_args = {}

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
        field_rules = getattr(flow_meta.on_start, "field_rules", [])
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
                    query_running_instance_num_by_tpl_id(flow_template_id)
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
        flow_meta.on_start(ctx, **start_flow_args)

        # 将状态更新到running
        self._flow_instance_dao.update_status(
            flow_instance.id, FlowStatus.STATUS_RUNNING)

        return Result.ok(data=flow_instance)

    @check(
        IntField("flow_instance_id", required=True),
        StrField("target_step", required=True),
        StrField("target_action", required=True),
        IntField("actor", required=True),
        Field("action_args", type_=dict, required=False,
              default=None, value_of=json.loads)
    )
    def handle_job_action(self, flow_instance_id: int,
                          target_step: str, target_action: str,
                          actor: int, action_args: Dict[str, Any]) -> Result:
        """处理Job中的Action

           S1. 检查并获取flow实例
           S2. 检查job以及job_action的存在性
           S3. 检查执行人是否合法
           S4. 检查当前是否可以允许该step及target_action的执行
           S5. 合并以及检查相关参数
           S6. 回调相关Action逻辑
           S7. 返回回调函数的返回值

           :param flow_instance_id: flow的标识
           :param target_step: 要执行的Step
           :param target_action: 自定义的动作名称
           :param actor: 执行人
           :param action_args: 执行该自定义动作所需要的参数
        """

        if action_args is None:
            action_args = {}

        # 检查flow instance的id合法性
        flow_instance = self._flow_instance_dao.query_by_instance_id(
            flow_instance_id)
        if flow_instance is None:
            raise BadReq("invalid_flow_instance",
                         flow_instance_id=flow_instance_id)

        # 检查flow instance的状态
        if flow_instance.status != FlowStatus.STATUS_RUNNING:
            raise BadReq("invalid_status", status=flow_instance.status)

        # 获取对应的flow template和flow meta
        flow_template = self._flow_tpl_dao\
            .query_flow_template_by_id(flow_instance.flow_template_id)
        if flow_template is None:
            raise BadReq("unknown_flow_template",
                         flow_template_id=flow_instance.flow_template_id)
        try:
            flow_meta = self._flow_meta_mgr.get(flow_template.flow_meta)
        except ObjectNotFoundException:
            raise BadReq("unknown_flow_meta", flow_meta=flow_meta)

        actor_info = self._user_dao.query_user_by_id(actor)
        if actor_info is None:
            raise BadReq("invalid_actor", actor=actor)

        # 检查当前step以及当前step是否完成
        # 检查下一个状态是否是目标状态
        handler_mtd, job_def, job_ref = self._check_step(
            flow_meta, flow_instance, target_step, target_action)

        # 合并检查参数 request_args - template_bind_args - meta_bind_args
        rs = self._check_and_combine_action_args(
            job_def, target_action, action_args, job_ref, flow_template)
        if rs.status_code == Result.STATUS_BADREQUEST:
            return rs

        job_instance = self._job_instance_dao.query_by_instance_id_and_step(
            instance_id=flow_instance_id,
            step=target_step
        )

        # 如果是trigger事件，需要创建job_instance记录
        if target_action == "trigger":
            job_instance = self._job_instance_dao.insert(
                flow_instance_id, target_step, actor)
            self._flow_instance_dao.update_current_step(
                flow_instance_id, target_step)

        action = self._job_action_dao.insert(
            job_instance_id=job_instance.id,
            action=target_action,
            actor=actor,
            arguments=action_args,
            data={}
        )

        ctx = MySQLContext(
            flow_executor=self,
            db=self._db,
            flow_instance_id=flow_instance.id,
            job_instance_id=job_instance.id,
            job_action_id=action.id,
            flow_meta=flow_meta,
            current_step=target_step
        )

        action_args = rs.data
        rs = handler_mtd(ctx, **action_args)
        if not isinstance(rs, Result):
            rs = Result.ok(data=rs)

        if not rs.is_success():
            # 如果返回结果不成功，那么允许重来
            self._job_action_dao.delete_by_id(action.id)

        return rs

    def _check_and_combine_action_args(
            self, job_def, target_action, request_args,
            job_ref, flow_template):

        job_arg_defines = job_def.job_args.get(target_action)

        # 无参数定义
        if not job_arg_defines:
            return Result.ok(data={})

        # 获取各级的参数绑定
        meta_bind_args = job_ref.bind_args.get(target_action, {})
        tpl_bind_args = flow_template.bind_args.get(
            job_ref.step_name, {}).get(target_action, {})

        args_chain = ChainMap(request_args, tpl_bind_args, meta_bind_args)

        # 最终生成使用的参数集合
        args = {}

        for job_arg_define in job_arg_defines:
            try:
                arg_name = job_arg_define.name

                # auto 类型，直接从chain中取值
                if job_arg_define.mark == JobArg.MARK_AUTO:
                    value = args_chain[arg_name]
                # static类型，从template中取值
                elif job_arg_define.mark == JobArg.MARK_STATIC:
                    value = tpl_bind_args.get(arg_name, None)
                # const类型，从meta中取值
                elif job_arg_define.mark == JobArg.MARK_CONST:
                    value = meta_bind_args.get(arg_name, None)

                args[arg_name] = job_arg_define.field_info(value)
            except InvalidFieldException as e:
                full_field_name = "{step}.{action}.{arg}".format(
                    step=job_ref.step_name,
                    action=target_action,
                    arg=arg_name
                )
                return self._gen_bad_req_result(e, full_field_name)

        return Result.ok(data=args)

    def _check_step(self, flow_meta, flow_instance,
                    target_step, target_action):
        current_step = flow_instance.current_step

        # 检查当前action的方法是否存在
        target_job_ref = flow_meta.get_job_ref_by_step_name(target_step)
        if target_job_ref is None:
            raise BadReq("unknown_target_step", target_step=target_step)
        try:
            job_def = self._job_mgr.get(target_job_ref.job_name)
        except ObjectNotFoundException:
            raise BadReq("unknown_job", job_name=target_job_ref.name)

        handler_mtd = getattr(job_def, "on_" + target_action, None)
        if handler_mtd is None:
            raise BadReq("unknown_action_handler", action=target_action)

        # 当前step即目标step
        if current_step == target_step:

            job_instance = self._job_instance_dao.\
                query_by_instance_id_and_step(
                    instance_id=flow_instance.id,
                    step=current_step
                )

            if job_instance.status == JobStatus.STATUS_FINISHED:
                raise BadReq("step_already_runned", step=target_step)

            # 检查当前action是否被执行过
            action = self._job_action_dao.\
                query_by_job_instance_id_and_action(
                    job_instance_id=job_instance.id,
                    action=target_action
                )

            if action is not None:
                raise BadReq("action_already_runned", action=target_action)

            # 如果非trigger，则检查trigger是否执行过
            if target_action != "trigger":
                trigger_action = self._job_action_dao.\
                    query_by_job_instance_id_and_action(
                        job_instance_id=job_instance.id,
                        action="trigger"
                    )
                if trigger_action is None:
                    raise BadReq("no_trigger")

            return handler_mtd, job_def, target_job_ref

        if current_step != "start":
            # 当前step非目标step
            job_instance = self._job_instance_dao.\
                query_by_instance_id_and_step(
                    instance_id=flow_instance.id,
                    step=current_step
                )

            # 流程记录了未知的current_step
            if job_instance is None:
                raise BadReq("unknown_current_step", current_step=current_step)

            # 当前的step尚未完成
            if job_instance.status != JobStatus.STATUS_FINISHED:
                raise BadReq("current_step_unfinished",
                             current_step=current_step)

        # 获取下一个该运行的步骤
        next_step = flow_meta.get_next_step(current_step)
        if next_step != target_step:
            raise BadReq("invalid_target_step", next_step=next_step)
        if target_action != "trigger":
            raise BadReq("no_trigger")

        return handler_mtd, job_def, target_job_ref

    def _combine_and_check_args(
            self, action_name, field_rules, *args_dict):
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
            full_field_name = "{action_name}.{field_name}".format(
                action_name=action_name,
                field_name=e.field_name
            )
            return self._gen_bad_req_result(e, full_field_name)
        else:
            return Result.ok(data=_combined_args)

    def _gen_bad_req_result(self, e, full_field_name):
        loc, _ = locale.getlocale(locale.LC_ALL)
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

    def _finish_step(self, ctx):
        """标记一个job instance完成，通常由action通过context进行回调
           S1. 将job_instance的状态更新为finish
           S2. 检查整个flow是否已经完成
           S3. 如果整个流程已经完成，那么标记flow_instance的status
           S4. 回调flow_meta中的on_finish事件
        """
        flow_instance_id, job_instance_id = (
            ctx.flow_instance_id,
            ctx.job_instance_id
        )

        self._job_instance_dao.update_status(
            job_instance_id=job_instance_id,
            status=JobStatus.STATUS_FINISHED
        )

        next_step = ctx.flow_meta.get_next_step(ctx.current_step)

        # 尚未完成，继续处理
        if next_step != "finish":
            return

        # 修改flow_instance的状态
        self._flow_instance_dao.update_status(
            flow_instance_id=flow_instance_id,
            status=FlowStatus.STATUS_FINISHED
        )

        # 回调on_finish事件
        on_finish_handler = getattr(ctx.flow_meta, "on_finish", None)
        if on_finish_handler is None:
            return
        on_finish_handler(ctx)

    def _stop_whole_flow(self, ctx):
        """终止整个flow的运行，通常由action通过context进行回调
           S1. 标记flow_instance的status为stop
           S2. 回调flow_meta中的on_stop事件
        """
        self._flow_instance_dao.update_status(
            flow_instance_id=ctx.flow_instance_id,
            status=FlowStatus.STATUS_STOPPED
        )

        # 回调on_stop事件
        on_stop_handler = getattr(ctx.flow_meta, "on_stop", None)
        if on_stop_handler is None:
            return
        on_stop_handler(ctx)
