class EasemobFlowException(Exception):

    """easemob-flow项目中所有的异常子类都需要继承此异常
    """

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg
