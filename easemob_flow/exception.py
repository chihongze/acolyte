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
