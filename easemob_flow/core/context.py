import collections
from abc import ABCMeta


class AbstractFlowContext(collections.Mapping, meta=ABCMeta):

    def __init__(self):
        pass
