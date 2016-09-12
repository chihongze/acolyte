import simplejson as json
from acolyte.core.job import (
    AbstractJob,
    JobArg,
)
from acolyte.util.validate import IntField, StrField


class EchoJob(AbstractJob):

    """该Job用于测试，打印事件和参数，并返回接收到的参数
    """

    def __init__(self):
        super().__init__("echo", "test job echo", job_args={
            "trigger": [
                JobArg("a", IntField("a", required=True),
                       JobArg.MARK_CONST, "a的值"),
                JobArg("b", IntField("b", required=True),
                       JobArg.MARK_STATIC, "b的值"),
            ],
            "finish": [
                JobArg("c", IntField("c", required=True),
                       JobArg.MARK_AUTO, "c的值")
            ],
            "stop": [
                JobArg("d", StrField("d", required=True, min_len=3),
                       JobArg.MARK_AUTO, "d的值"),
                JobArg("e", StrField("e", required=True, max_len=20),
                       JobArg.MARK_AUTO, "e的值")
            ],
        })

    def on_trigger(self, context, arguments):
        print("on trigger events, received args: {}".format(
            json.dumps(arguments)))
        return arguments


class OldManJob(AbstractJob):

    """Mock Job 长者Job
    """

    def __init__(self):
        super().__init__("old_man", "old man job")

    def on_trigger(self, context, arguments):
        print("任何事情都要按照基本法，按照选举法！我没有要钦定！没有任何这个意思！")
        return "trigger"


def letter_job_meta(letter):

    class LetterJobMeta(type):

        def __new__(cls, name, bases, attrs):

            def _make_method(action):
                def method(self, context, arguments):
                    print("{action}: {letter}".format(
                        action=action, letter=letter))
                    return "{action}_{letter}".format(
                        action=action, letter=letter)
                return method

            attrs["on_trigger"] = _make_method("trigger")
            attrs["__init__"] = lambda self: AbstractJob.__init__(
                self, "job_" + letter, "job " + letter)

            bases += (AbstractJob,)

            return type(name, bases, attrs)

    return LetterJobMeta


class AJob(metaclass=letter_job_meta("A")):
    pass


class BJob(metaclass=letter_job_meta("B")):
    pass


class CJob(metaclass=letter_job_meta("C")):
    pass


class DJob(metaclass=letter_job_meta("D")):
    pass
