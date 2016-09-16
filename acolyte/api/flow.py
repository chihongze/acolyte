handlers = [

    # get flow meta info
    {
        "url": "/v1/flow/meta/([a-zA-Z0-9]+)",
        "http_method": "get",
        "service": "FlowService",
        "method": "get_flow_meta_info",
        "path_variables": [
            "flow_meta_name",
        ]
    }

]
