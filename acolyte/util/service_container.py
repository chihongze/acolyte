from acolyte.exception import (
    EasemobFlowException,
    ObjectAlreadyExistedException,
    ObjectNotFoundException,
    InvalidArgumentException
)
from acolyte.util import log
from acolyte.util.lang import get_full_class_name
from acolyte.core.service import AbstractService


class ServiceContainer:

    """所有服务性质的对象都可以通过该容器去注册，
       可以通过该容器来获取需要依赖的服务
    """

    def __init__(self):
        self._container = {}

    def register(self, service_id, service_obj,
                 init_callback=None, lazy=False):
        """将服务对象注册到容器
           :param service_id: 服务对象标识，要求系统全局唯一
           :param service_obj: 服务对象，可以是函数，模块或者其它什么东西，依赖者知道就行。
           :param init_callback: 初始化函数
           :param lazy: 是否是懒加载
        """
        if service_id in self._container:
            raise ObjectAlreadyExistedException(service_id)
        service_defination = ServiceDefination(
            service_id, service_obj, init_callback, lazy)
        if not lazy:
            service_defination.init()
        self._container[service_id] = service_defination

        log.acolyte.debug((
            "register service {service_id} -> {service_class} to container"
        ).format(service_id=service_id,
                 service_class=get_full_class_name(service_obj.__class__)))

    def register_service(self, service_class, init_callback=None, lazy=False):
        """该方法专门用于facade服务对象的注册
           :param service_class: 服务对象类型
           :param init_callback: 初始化函数
           :param lazy: 是否是懒加载
        """
        if not issubclass(service_class, AbstractService):
            raise InvalidArgumentException(
                "the service class must be the subclass of AbstractService")

        self.register(
            service_id=service_class.__name__,
            service_obj=service_class(self),
            init_callback=init_callback,
            lazy=lazy
        )

    def get_service(self, service_id):
        """从容器中获取服务
           :param service_id: 服务对象标识
        """
        if service_id not in self._container:
            raise ObjectNotFoundException(service_id)
        service_define = self._container[service_id]
        if not service_define.has_inited():
            service_define.init()
        return service_define.service_obj

    def after_register(self):
        for service in self._container.values():
            service.after_register()


class ServiceDefination:

    """服务相关的meta数据
    """

    def __init__(self, service_id, service_obj,
                 init_callback=None, lazy=False):

        self._service_id = service_id
        self._service_obj = service_obj
        self._init_callback = init_callback
        self._lazy = lazy
        self._inited = False

    @property
    def service_id(self):
        return self._service_id

    @property
    def service_obj(self):
        return self._service_obj

    @property
    def init_callback(self):
        return self._init_callback

    @property
    def lazy(self):
        return self._lazy

    def has_inited(self):
        """是否已经初始化
        """
        return self._inited

    def init(self):
        """执行初始化
        """
        if self._inited:
            # 已经初始化了，抛出异常
            raise ServiceAlreadyInitedException(self._service_id)

        if self._init_callback is not None:
            self._init_callback(self._service_obj)
        self._lazy = True

    def after_register(self):
        """当容器注册完成之后，回调该方法
        """
        if not hasattr(self._service_obj, "_after_register"):
            return
        self._service_obj._after_register()


class ServiceAlreadyInitedException(EasemobFlowException):

    def __init__(self, service_id):
        super().__init__(
            "Service '{service_id}' already inited.".format(service_id))
