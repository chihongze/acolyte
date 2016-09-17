handlers = [

    # get all flow meta
    {
        "url": "/v1/flow/meta/_all",
        "http_method": "get",
        "service": "FlowService",
        "method": "get_all_flow_meta",
    },

    # get flow meta info by meta name
    {
        "url": "/v1/flow/meta/([a-zA-Z0-9_]+)",
        "http_method": "get",
        "service": "FlowService",
        "method": "get_flow_meta_info",
        "path_variables": [
            "flow_meta_name",
        ]
    },

    # create flow template
    {
        "url": "/v1/flow/template",
        "http_method": "put",
        "service": "FlowService",
        "method": "create_flow_template",
        "body_variables": {
            "flow_meta_name": "flow_meta_name",
            "name": "name",
            "bind_args": "bind_args",
            "max_run_instance": "max_run_instance",
        },
        "context_variables": {
            "current_user_id": "creator"
        }
    }

]
