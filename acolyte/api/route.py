"""本模块用于声明REST API URL地址到handler的映射
"""
from acolyte.api.flow import GetFlowMetaInfoHandler


URL_MAPPING = [
    (r"/v1/flow/meta/([a-zA-Z0-9_]+)", GetFlowMetaInfoHandler)
]
