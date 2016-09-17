"""本模块用于声明REST API URL地址到handler的映射
"""

from acolyte.api import (
    flow,
)
from acolyte.api import APIHandlerBuilder


URL_MAPPING = [

]

_handler_modules = (flow, )

for handler_module in _handler_modules:
    handlers = getattr(handler_module, "handlers", [])
    for handler in handlers:
        builder = APIHandlerBuilder(
            service_id=handler["service"],
            method_name=handler["method"],
            http_mtd=handler["http_method"]
        )

        # 绑定path变量
        path_variables = handler.get("path_variables", [])
        for idx, path_variable in enumerate(path_variables):
            if isinstance(path_variable, str):
                builder.bind_path_var(idx + 1, path_variable)
            else:
                builder.bind_path_var(idx + 1, *path_variable)

        # 绑定body变量
        body_variables = handler.get("body_variables", {})
        for body_var_name, arg_info in body_variables.items():
            if isinstance(arg_info, str):
                builder.bind_body_var(body_var_name, arg_info)
            else:
                builder.bind_body_var(body_var_name, *arg_info)

        # 绑定上下文变量
        context_variables = handler.get("context_variables", {})
        for context_var_name, arg_info in context_variables.items():
            if isinstance(arg_info, str):
                builder.bind_context_var(context_var_name, arg_info)
            else:
                builder.bind_context_var(context_var_name, *arg_info)

        URL_MAPPING.append((handler["url"], builder.build()))
