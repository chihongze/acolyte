"""该模块用于维护服务消息
   local_code => service_id => service_method => error_reason
"""
messages = {
    "C/zh_CN": {


        "flow_service": {
            "flow_executor_service": {
                "template_not_found": "找不到ID为'{tpl_id}'的模板"
            },

            "get_flow_meta_info": {
                "flow_meta_not_exist": "找不到名称为'{flow_meta}'的FlowMeta"
            },

            "create_flow_template": {
                "invalid_max_run_instance": "运行实例数目必须是大于等于0的正整数",
                "name_already_exist": "flow template '{name}' 已存在",
                "invalid_creator_id": "创建者ID '{creator}' 不合法",
            }
        }


    }
}
