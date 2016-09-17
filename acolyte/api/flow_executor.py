handlers = [

    # start a flow instance
    {
        "url": r"/v1/flow/template/(\d+)/start",
        "http_method": "post",
        "service": "FlowExecutorService",
        "method": "start_flow",
        "path_variables": [
            "flow_template_id"
        ],
        "body_variables": {
            "description": "description",
            "start_flow_args": "start_flow_args",
        },
        "context_variables": {
            "current_user_id": "initiator"
        }
    },

    # run an action of the job
    {
        "url": r"/v1/flow/instance/(\d+)/([\w_]+)/([\w_]+)",
        "http_method": "post",
        "service": "FlowExecutorService",
        "method": "handle_job_action",
        "path_variables": [
            "flow_instance_id",
            "target_step",
            "target_action"
        ],
        "body_variables": {
            "action_args": "action_args"
        },
        "context_variables": {
            "current_user_id": "actor"
        }
    }

]
