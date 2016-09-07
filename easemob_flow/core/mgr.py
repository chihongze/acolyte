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
