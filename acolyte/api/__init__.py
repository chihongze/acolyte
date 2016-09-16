from abc import ABCMeta
import simplejson as json
from functools import wraps
from tornado.web import RequestHandler
from acolyte.util.json import to_json


class BaseAPIHandler(RequestHandler, metaclass=ABCMeta):

    def __init__(self, application, request):
        super().__init__(application, request)

    def _(self, service_id):
        return BaseAPIHandler.service_container.get_service(service_id)

    def json_body(self):
        body = self.request.body
        if not body:
            return {}
        return json.loads(self.request.body)


def response_json(func):

    @wraps(func)
    def _func(self, *args, **kwds):
        rs = func(self, *args, **kwds)
        self.set_header('Content-Type', 'application/json;charset=utf-8')
        self.set_status(rs.status_code)
        self.write(to_json(rs))
        self.finish()

    return _func


class APIHandlerBuilder:

    """该类创建的Builder对象可以由Service方法自动创建出
       对应的APIHandler
    """

    def __init__(self, service_id, method_name, http_mtd):
        self._service_id = service_id
        self._method_name = method_name
        self._http_mtd = http_mtd
        self._bind_path_vars = {}
        self._bind_body_vars = {}

    def bind_path_var(self, path_var_index, mtd_arg_name, handler=None):
        """将tornado的path variable绑定到service方法的参数上
           :param path_var_index: path variable的索引，从1计数
           :param mtd_arg_name: 方法参数名
        """
        self._bind_path_vars[path_var_index] = mtd_arg_name, handler
        return self

    def bind_body_vars(self, body_var_name, mtd_arg_name, handler=None):
        """将body中的值提取出来，绑定到service方法的参数上
           :param body_var_name: body参数名称
           :param mtd_arg_name: 方法参数名
        """
        self._bind_body_vars[body_var_name] = mtd_arg_name, handler
        return self

    def build(self):
        """执行最终构建
        """
        bases = (BaseAPIHandler,)
        attrs = {}

        _bind_path_vars = self._bind_path_vars
        _bind_body_vars = self._bind_body_vars
        _service_id = self._service_id
        _method_name = self._method_name

        def handler(self, *args):

            nonlocal _bind_path_vars
            nonlocal _bind_body_vars
            nonlocal _service_id
            nonlocal _method_name

            service_args = {}

            # 填充path variable
            for idx, val in enumerate(args, start=1):
                mtd_arg_name, handler = _bind_path_vars[idx]
                service_args[mtd_arg_name] = val if handler is None \
                    else handler(val)

            # 填充body variable
            json_body = self.json_body()
            for body_var_name, (mtd_arg_name, handler) in \
                    _bind_body_vars.items():
                val = json_body.get(body_var_name)
                service_args[mtd_arg_name] = val if handler is None \
                    else handler(val)

            rs = getattr(self._(_service_id), _method_name)(**service_args)
            self.set_header('Content-Type', 'application/json;charset=utf-8')
            self.set_status(rs.status_code)
            self.write(to_json(rs))
            self.finish()

        attrs[self._http_mtd] = handler

        class_name = self.mtd_name_to_class_name()
        return type(class_name, bases, attrs)

    def mtd_name_to_class_name(self):
        str_buf = []
        for idx, char in enumerate(self._method_name):
            # 第一个字母大写
            if idx == 0 or self._method_name[idx - 1] == '_':
                str_buf.append(char.upper())
            elif char != '_':
                str_buf.append(char.lower())
        return "".join(str_buf) + "Handler"
