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
