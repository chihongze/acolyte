from acolyte.api import APIHandlerBuilder

GetFlowMetaInfoHandler = APIHandlerBuilder(
    "FlowService", "get_flow_meta_info", "get").\
    bind_path_var(1, "flow_meta_name").build()
