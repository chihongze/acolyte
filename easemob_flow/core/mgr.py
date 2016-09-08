import pkg_resources
from abc import ABCMeta, abstractmethod
from easemob_flow.exception import EasemobFlowException


class AbstractManager(meta=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def load(self):
        """加载所有对象到容器
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


class ObjectNotFoundException(EasemobFlowException):

    """找不到对象
    """

    def __init__(self, object_name):
        super().__init__("Object '{name}' not found.".format(name=object_name))


class EntryPointManager(AbstractManager):

    def __init__(self, entry_point):
        super().__init__()
        self._entry_point = entry_point
        self._container = {}

    def load(self):
        for ep in pkg_resources.iter_entry_points(self._entry_point):
            self._container[ep.name] = ep.load()

    def get(self, name):
        try:
            return self._container[name]
        except KeyError:
            raise ObjectNotFoundException(name)

    def all(self):
        return self._container.values()

# managers for job and flow_meta
job_manager = EntryPointManager("easemob_flow.job")
flow_meta_manager = EntryPointManager("easemob_flow.flow_meta")
