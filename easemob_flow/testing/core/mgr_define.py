"""该模块用于构建测试用的各种mgr
"""

from easemob_flow.testing.core.job import (
    EchoJob,
    OldManJob,
    AJob,
    BJob,
    CJob,
    DJob,
)
from easemob_flow.core.mgr import DictBasedManager
from easemob_flow.core.job import JobRef, JobArg
from easemob_flow.core.flow import FlowMeta


class TestFlowMeta(FlowMeta):

    def __init__(self):
        super().__init__(
            name="test_flow",
            description="just a test flow",
            jobs=(
                JobRef(
                    name="echo",
                    trigger=[

                    ],
                    finish=[

                    ],
                    stop=[

                    ]
                ),
                JobRef(
                    name="old_man",
                ),
                JobRef(
                    name="job_A"
                ),
                JobRef(
                    name="job_B"
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

    def on_start(self, context, arguments):
        pass

    def on_stop(self, context, arguments):
        pass

    def on_finish(self, context, arguments):
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
