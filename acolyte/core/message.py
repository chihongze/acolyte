"""该模块用于维护服务消息
   local_code => service_id => service_method => error_reason
"""

# 各个服务接口的提示消息
messages = {
    "C/zh_CN": {


        "FlowService": {
            "flow_executor_service": {
                "template_not_found": "找不到ID为'{tpl_id}'的模板"
            },

            "get_flow_meta_info": {
                "flow_meta_name_empty": "flow_meta_name参数不能为空",
                "flow_meta_name_invalid_type": "flow_meta_name参数只允许字符串类型",
                "flow_meta_not_exist": "找不到名称为'{flow_meta}'的FlowMeta"
            },

            "create_flow_template": {
                "flow_meta_not_exist": "指定的flow meta对象'{flow_meta}'不存在",
                "name_already_exist": "flow template '{name}' 已存在",
                "invalid_creator_id": "创建者ID '{creator}' 不合法",
                "not_allow_bind_const": "参数 '{arg_name}' 是const类型，不允许被覆盖"
            }
        },

        "FlowExecutorService": {
            "start_flow": {
                "invalid_flow_template":
                "不合法的flow template id: {flow_template_id}",
                "invalid_flow_meta": "不合法的flow meta: {flow_meta}",
                "invalid_initiator": "不合法的发起者ID: {initiator}",
                "too_many_instance":
                "无法创建更多的运行时实例，允许最大实例数目为: {allow_instance_num}"
            },
            "handle_job_action": {
                "invalid_flow_instance":
                "不合法的flow instance id: {flow_instance_id}",
                "invalid_status": "当前flow instance的状态为 '{status}'，无法执行action",
                "unknown_flow_template":
                "找不到对应的flow template: {flow_template_id}",
                "unknown_flow_meta": "找不到对应的flow meta: '{flow_meta}'",
                "invalid_actor": "不合法的actor id '{actor}'",
                "unknown_target_step": "未知的target step: '{target_step}'",
                "unknown_job": "未知的Job引用 '{job_name}'",
                "unknown_action_handler": "找不到action handler: '{action}'",
                "step_already_runned": "step '{step}' 已经被运行过了",
                "action_already_runned": "该action已经被运行过了",
                "no_trigger": "尚未执行trigger action",
                "unknown_current_step": "当前step未知: '{current_step}'",
                "current_step_unfinished": "当前step '{current_step}' 尚未完成",
                "invalid_target_step": "下一个目标step为 '{next_step}'",
            }
        },

        "UserService": {

            "login": {
                "no_match": "账号密码不匹配",
            },

            "add_user": {
                "email_exist": "邮箱'{email}'已经存在",
                "role_not_found": "指定的角色编号'{role}'不存在",
                "operator_not_found": "操作人信息不合法",
                "not_allow_operation": "您无权进行此项操作",
            },

            "check_token": {
                "invalid_token": "不合法的token"
            }
        },


    }
}

# 字段验证的默认提示消息
default_validate_messages = {
    "C/zh_CN": {
        "empty": "{field_name}参数不能为空",
        "invalid_type": "{field_name}参数只接受{expect}类型",
        "less_than_min": "{field_name}参数不能小于{expect}",
        "more_than_max": "{field_name}参数不能大于{expect}",
        "less_than_min_length": "{field_name}的长度不能小于{expect}",
        "more_than_max_length": "{field_name}的长度不能大于{expect}",
        "invalid_format": "{field_name}的格式不满足正则表达式'{expect}'"
    }
}
