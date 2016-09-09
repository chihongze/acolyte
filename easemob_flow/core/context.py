import collections
from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty
)


class AbstractFlowContext(collections.Mapping, metaclass=ABCMeta):

    """上下文对象用于在Flow运行中的Job之间传递数据
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def save(self, data):
        pass

    @abstractproperty
    def current_step(self):
        pass

    @abstractproperty
    def current_action(self):
        pass
