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
                JobRef(
                    step_name="job_B",
                    job_name="job_B"
                ),
            ),
            start_args={
                "x": -1,
                "y": -2
            },
            stop_args={
                "z": -3,
            },
        )

    @declare_args(
        IntField("x", required=True),
        IntField("y", required=True)
    )
    def on_start(self, context, x, y):
        pass

    @declare_args(
        IntField("z", required=True)
    )
    def on_stop(self, context, z):
        pass

    def on_finish(self, context):
        pass

    def on_exception(self, context, exc_type, exc_value, tb):
        pass

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
