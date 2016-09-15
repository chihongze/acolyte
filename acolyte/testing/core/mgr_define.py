"""该模块用于构建测试用的各种mgr
"""

from acolyte.testing.core.job import (
    EchoJob,
    OldManJob,
    AJob,
    BJob,
    CJob,
    DJob,
)
from acolyte.core.mgr import DictBasedManager
from acolyte.core.job import JobRef
from acolyte.core.flow import FlowMeta
from acolyte.util.validate import (
    IntField,
    declare_args
)


class TestFlowMeta(FlowMeta):

    def __init__(self):
        super().__init__(
            name="test_flow",
            description="just a test flow",
            jobs=(
                JobRef(
                    step_name="echo",
                    job_name="echo",
                    trigger={
                        "a": 5
                    },
                    finish={

                    },
                    stop={

                    }
                ),
                JobRef(
                    step_name="old_man",
                    job_name="old_man"
                ),
                JobRef(
                    step_name="job_A",
                    job_name="job_A"
                ),
            ),
            start_args={
                "x": -1,
                "y": -2
            },
        )

    @declare_args(
        IntField("x", required=True),
        IntField("y", required=True)
    )
    def on_start(self, context, x, y):
        print("start the workflow, x = {x}, y = {y}".format(
            x=x,
            y=y
        ))

    def on_stop(self, context):
        print("the whole workflow stopped")

    def on_finish(self, context):
        print("the whole workflow finished")

# 构建测试使用的容器


flow_meta_mgr = DictBasedManager()
test_flow_meta = TestFlowMeta()
flow_meta_mgr.register(test_flow_meta.name, test_flow_meta)

job_mgr = DictBasedManager()
echo_job = EchoJob()
job_mgr.register(echo_job.name, echo_job)
old_man_job = OldManJob()
job_mgr.register(old_man_job.name, old_man_job)
for job_type in (AJob, BJob, CJob, DJob):
    job = job_type()
    job_mgr.register(job.name, job)
