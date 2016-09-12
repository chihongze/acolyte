"""本模块包含跟flow相关的facade接口
"""

import simplejson as json
import datetime
import locale
from easemob_flow.util.validate import (
    Field,
    IntField,
    StrField,
    check,
    BadReq,
    InvalidFieldException
)
from easemob_flow.util.lang import get_from_nested_dict
from easemob_flow.core.service import (
    AbstractService,
    Result
)
from easemob_flow.core.mgr import ObjectNotFoundException
from easemob_flow.core.storage.flow_template import FlowTemplateDAO
from easemob_flow.core.storage.user import UserDAO
from easemob_flow.core.view import (
    FlowMetaView,
    FlowTemplateView
)
from easemob_flow.core.job import JobArg
from easemob_flow.core.message import default_validate_messages


class FlowService(AbstractService):

    def __init__(self, service_container):
        super().__init__(service_container)

    def _after_register(self):
        # 注入两个manager
        self._flow_meta_mgr = self._("flow_meta_manager")
        self._job_mgr = self._("job_manager")
        db = self._("db")
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

    @check(
        StrField("flow_meta_name", required=True),
    )
    def get_flow_meta_info(self, flow_meta_name) -> Result:
        """获取单个的flow_meta详情
        """

        try:
            flow_meta = self._flow_meta_mgr.get(flow_meta_name)
        except ObjectNotFoundException:
            raise BadReq("flow_meta_not_exist", flow_meta=flow_meta_name)

        return Result.ok(data=FlowMetaView.from_flow_meta(
            flow_meta, self._job_mgr))

    @check(
        StrField("flow_meta_name", required=True),
        StrField("name", required=True, min_len=3, max_len=50,
                 regex="^[a-zA-Z0-9_]+$"),
        Field("bind_args", type_=dict, required=True, value_of=json.loads),
        IntField("max_run_instance", required=True, min_=0),
        IntField("creator", required=True)
    )
    def create_flow_template(self, flow_meta_name, name, bind_args,
                             max_run_instance, creator) -> Result:
        """创建flow_template
        """

        # 获取flow_meta以及检查其存在性
        try:
            flow_meta = self._flow_meta_mgr.get(flow_meta_name)
        except ObjectNotFoundException:
            raise BadReq("flow_meta_not_exist", flow_meta=flow_meta_name)

        # 检查name是否已经存在
        if self._flow_tpl_dao.is_name_existed(name):
            raise BadReq("name_already_exist", name=name)

        # 检查creator是否存在
        creator_user = self._user_dao.query_user_by_id(creator)
        if not creator_user:
            raise BadReq("invalid_creator_id", creator=creator)

        # 校验参数
        rs = self._validate_tpl_bind_args(flow_meta, bind_args)
        if rs.status_code == Result.STATUS_BADREQUEST:
            return rs
        bind_args = rs.data

        created_on = datetime.datetime.now()

        # 插入吧!
        flow_template = self._flow_tpl_dao.insert_flow_template(
            flow_meta_name, name, json.dumps(bind_args),
            max_run_instance, creator, created_on)

        # 返回刚创建的View
        return Result.ok(
            data=FlowTemplateView.from_flow_template(
                flow_template, creator_user))

    # 校验template的绑定参数
    def _validate_tpl_bind_args(self, flow_meta, bind_args):
        new_bind_args = {}

        for job_ref in flow_meta.jobs:

            job = self._job_mgr.get(job_ref.name)
            new_bind_args[job.name] = {}

            for event, job_arg_declares in job.job_args.items():

                new_bind_args[job.name][event] = {}

                for job_arg_declare in job_arg_declares:

                    try:

                        bind_value = get_from_nested_dict(
                            bind_args, job.name, event, job_arg_declare.name)

                        # const 类型的参数不允许被绑定
                        if job_arg_declare.mark == JobArg.MARK_CONST:
                            continue

                        # 执行校验并替换新值
                        new_value = job_arg_declare.field_info(bind_value)
                        new_bind_args[job.name][event][
                            job_arg_declare.name] = new_value

                    except InvalidFieldException as e:

                        field_name = "{job_name}_{event}_{arg_name}".format(
                            job_name=job.name,
                            event=event,
                            arg_name=job_arg_declare.name
                        )
                        full_reason = "{field_name}_{reason}".format(
                            field_name=field_name,
                            reason=e.reason
                        )

                        # 产生错误消息
                        loc, _ = locale.getlocale(locale.LC_ALL)
                        msg = default_validate_messages[loc][e.reason]
                        if e.expect is None:
                            msg = msg.format(field_name=field_name)
                        else:
                            msg = msg.format(
                                field_name=field_name, expect=e.expect)

                        return Result.bad_request(full_reason, msg=msg)

        return Result.ok(data=new_bind_args)

    def get_all_flow_templates(self):
        """获取所有的flow_templates列表
        """
        all_flow_templates = self._flow_tpl_dao.query_all_templates()
        if not all_flow_templates:
            return Result.ok(data=[])
        users = self._user_dao.query_users_by_id_list(
            [tpl.creator for tpl in all_flow_templates], to_dict=True)
        templates_view = [FlowTemplateView.from_flow_template(
            tpl, users[tpl.creator]) for tpl in all_flow_templates]
        return Result.ok(data=templates_view)

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
