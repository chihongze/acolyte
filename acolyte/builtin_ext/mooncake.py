"""抢月饼，你懂的
"""

from acolyte.core.job import (
    AbstractJob,
    JobArg,
    JobRef
)
from acolyte.core.flow import FlowMeta
from acolyte.core.service import Result
from acolyte.util.validate import IntField, StrField


class ProgrammerJob(AbstractJob):

    def __init__(self):
        super().__init__(
            name="programmer",
            description=(
                "我是一个程序员，"
                "我的爱好是抢月饼！"
            ),
            job_args={
                "midautumn": [

                    JobArg(
                        "cake_num",
                        IntField(
                            "cake_num", required=False, default=1, min_=1),
                        mark=JobArg.MARK_AUTO,
                        comment="抢到的月饼数目",
                    ),

                ]
            }
        )

    def on_trigger(self, context):
        return Result.ok(data="好吧，我要开始加班还房贷了")

    def on_midautumn(self, context, cake_num):
        context.finish()
        return Result.ok(data="我抢了{cake_num}个月饼".format(cake_num=cake_num))


class HRJob(AbstractJob):

    def __init__(self):
        super().__init__(
            name="hr",
            description=(
                "我是一个HR，"
                "我专门跟抢月饼的程序员过不去。"
            ),
            job_args={
                "found": [

                    JobArg(
                        "who",
                        StrField("who", required=True, regex=r'^\w+$'),
                        mark=JobArg.MARK_AUTO,
                        comment="抢月饼的人",
                    )
                ]
            }
        )

    def on_trigger(self, context):
        return Result.ok(data="刚才好像有人抢了月饼")

    def on_found(self, context, who):
        context.finish()
        return Result.ok(data="是{who}在抢月饼，我要去报告老板!".format(who=who))


class BossJob(AbstractJob):

    def __init__(self):
        super().__init__(
            name="boss",
            description=(
                "我是老板，"
                "我的心情即公司价值观"
            ),
            job_args={
                "hr_report": [
                    JobArg(
                        "mood",
                        StrField("mood", required=True),
                        mark=JobArg.MARK_AUTO,
                        comment="老板心情",
                    )
                ]
            }
        )

    def on_trigger(self, context):
        return Result.ok(data="这个世界不是因为你能做什么，而是你该做什么。")

    def on_hr_report(self, context, mood):
        if mood == "好":
            context.finish()
            return Result.ok(data="Geek文化嘛，多大点儿事")
        else:
            context.stop()
            return Result.ok(data="不诚信，违反价值观，严肃处理")


class MooncakeFlowMeta(FlowMeta):

    def __init__(self):
        super().__init__(
            name="mooncake_flow",
            description="抢月饼flow",
            jobs=(
                JobRef(
                    step_name="programmer",
                    job_name="programmer"
                ),
                JobRef(
                    step_name="hr",
                    job_name="hr"
                ),
                JobRef(
                    step_name="boss",
                    job_name="boss"
                )
            )
        )

    def on_start(self, context):
        pass

    def on_stop(self, context):
        pass

    def on_finish(self, context):
        pass
