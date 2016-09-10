class EasemobFlowException(Exception):

    """easemob-flow项目中所有的异常子类都需要继承此异常
    """

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class UnsupportOperationException(EasemobFlowException):

    """如果对象不支持某个操作，可以抛出该异常
    """

    @classmethod
    def build(cls, clazz, operation):
        return UnsupportOperationException(
            "{clazz} not support operation: {opt}".format(
                clazz=clazz.__name__,
                opt=operation))

    def __init__(self, msg):
        super().__init__(msg)


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


class InvalidStatusException(EasemobFlowException):

    """操作状态发生问题时抛出此异常
    """

    def __init__(self, msg):
        super().__init__(msg)


class InvalidArgumentException(EasemobFlowException):

    """当传递的参数不合法时抛出此异常
    """

    def __init__(self, msg):
        super().__init__(msg)
