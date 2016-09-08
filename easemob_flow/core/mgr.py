import pkg_resources
from abc import ABCMeta, abstractmethod
from easemob_flow.exception import (
    EasemobFlowException,
    UnsupportOperationException
)


class AbstractManager(meta=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def load(self):
        """加载所有对象到容器
        """
        pass

    @abstractmethod
    def register(self, name, obj):
        """注册对象到容器
        """
        pass

    @abstractmethod
    def get(self, name):
        """从容器中获取元素
        """
        pass

    @abstractmethod
    def all(self):
        """获取容器中的所有元素信息
        """
        pass


class ManagerChain(AbstractManager):

    def __init__(self, *mgr_list):
        self._mgr_list = mgr_list

    def load(self):
        map(lambda mgr: mgr.load(), self._mgr_list)

    def register(self, name, obj):
        raise UnsupportOperationException.build(ManagerChain, "register")

    def get(self, name):
        for mgr in self._mgr_list:
            try:
                return mgr.get(name)
            except ObjectNotFoundException:
                continue
            else:
                raise ObjectNotFoundException(name)

    def all(self):
        result = []
        for mgr in self._mgr_list:
            result += mgr.all()
        return result


class DictBasedManager(AbstractManager):

    def __init__(self):
        super().__init__()
        self._container = {}

    def load(self):
        raise UnsupportOperationException(DictBasedManager, "load")

    def register(self, name, obj):
        if name in self._container:
            raise ObjectAlreadyExistedException(name)
        self._container[name] = obj

    def get(self, name):
        try:
            return self._container[name]
        except KeyError:
            raise ObjectNotFoundException(name)

    def all(self):
        return self._container.values()


class EntryPointManager(AbstractManager):

    def __init__(self, entry_point):
        super().__init__()
        self._entry_point = entry_point
        self._container = {}

    def load(self):
        for ep in pkg_resources.iter_entry_points(self._entry_point):
            self._container[ep.name] = ep.load()

# managers for job and flow_meta
job_manager = EntryPointManager("easemob_flow.job")
flow_meta_manager = EntryPointManager("easemob_flow.flow_meta")


class ObjectNotFoundException(EasemobFlowException):

    """找不到对象
    """

    def __init__(self, object_name):
        super().__init__("Object '{name}' not found.".format(name=object_name))


class ObjectAlreadyExistedException(EasemobFlowException):

    """重复在同一个manager当中注册相同的对象时抛出此异常
    """

    def __init__(self, object_name):
        super().__init__(
            "Object '{name}' already registered.".format(name=object_name))
