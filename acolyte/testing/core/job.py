from acolyte.core.job import (
    AbstractJob,
    JobArg,
)
from acolyte.core.service import Result
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
            "multiply": [
                JobArg("c", IntField("c", required=True),
                       JobArg.MARK_AUTO, "c的值")
            ],
            "minus": [
                JobArg("d", IntField("d", required=True),
                       JobArg.MARK_AUTO, "d的值"),
                JobArg("e", IntField("e", required=True),
                       JobArg.MARK_AUTO, "e的值")
            ],
        })

    def on_trigger(self, context, a, b):
        print("I received args: a={a}, b={b}".format(
            a=a,
            b=b
        ))
        r = a + b
        context["add_result"] = r
        return Result.ok(data=r)

    def on_multiply(self, context, c):
        print("I received args: c={c}".format(c=c))
        r = int(context["add_result"]) * c
        context["multiply_result"] = r
        return Result.ok(data=r)

    def on_minus(self, context, d, e):
        print("I received args: d={d}, e={e}".format(d=d, e=e))
        r = int(context["multiply_result"]) - d - e
        context.finish()
        return Result.ok(data=r)


class OldManJob(AbstractJob):

    """Mock Job 长者Job
    """

    def __init__(self):
        super().__init__("old_man", "old man job", job_args={
            "question": [
                JobArg("question", StrField(
                    "question", required=True), JobArg.MARK_AUTO, "向长者提问"),
            ]
        })

    def on_trigger(self, context):
        print("old man job on trigger")
        return Result.ok(data="跑的比谁都快")

    def on_question(self, context, question):
        if question == "董先森连任好不好啊":
            context.finish()
            return Result.ok(data="吼啊")
        else:
            return Result.bad_request("old_man_angry", msg="无可奉告")

    def on_angry(self, context):
        print("I'm angry! 你们这样子是不行的！我要终止整个flow！")
        context.stop()
        return Result.bad_request("old_man_angry", msg="I'm angry!")


def letter_job_meta(letter):

    class LetterJobMeta(type):

        def __new__(cls, name, bases, attrs):

            def _make_method(action):
                def method(self, context, x, y):
                    context.finish()
                    return Result.ok(data=(x + y))
                return method

            attrs["on_trigger"] = _make_method("trigger")
            attrs["__init__"] = lambda self: AbstractJob.__init__(
                self, "job_" + letter, "job " + letter, job_args={
                    "trigger": [
                        JobArg("x", IntField("x", required=True),
                               JobArg.MARK_AUTO, "arg x"),
                        JobArg("y", IntField("y", required=True),
                               JobArg.MARK_AUTO, "arg y")
                    ]
                })

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
