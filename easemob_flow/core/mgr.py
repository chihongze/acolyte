import pkg_resources
from abc import ABCMeta, abstractmethod
from easemob_flow.exception import (
    UnsupportOperationException,
    ObjectAlreadyExistedException,
    ObjectNotFoundException
)


class AbstractManager(metaclass=ABCMeta):

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

    def register(self, name: str, obj: object):
        raise UnsupportOperationException.build(ManagerChain, "register")

    def get(self, name: str) -> object:
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
        raise UnsupportOperationException.build(DictBasedManager, "load")

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


class EntryPointManager(DictBasedManager):

    def __init__(self, entry_point: str):
        super().__init__()
        self._entry_point = entry_point
        self._container = {}

    def load(self):
        for ep in pkg_resources.iter_entry_points(self._entry_point):
            obj = ep.load()
            self._container[obj.name] = obj

# managers for job and flow_meta
job_manager = EntryPointManager("easemob_flow.job")
flow_meta_manager = EntryPointManager("easemob_flow.flow_meta")
