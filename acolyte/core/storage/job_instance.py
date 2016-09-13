import datetime
from acolyte.core.storage import AbstractDAO
from acolyte.core.job import JobInstance, JobStatus


def _mapper(result):
    result["id_"] = result.pop("id")
    return JobInstance(**result)


class JobInstanceDAO(AbstractDAO):

    def __init__(self, db):
        super().__init__(db)

    def query_by_id(self, instance_id):
        return self._db.query_one((
            "select * from job_instance where id = %s"
        ), (instance_id,), _mapper)

    def query_by_instance_id_and_step(self, instance_id, step):
        return self._db.query_one((
            "select * from job_instance where "
            "flow_instance_id = %s and step_name = %s limit 1"
        ), (instance_id, step), _mapper)

    def insert(self, flow_instance_id, step_name, trigger_actor):
        now = datetime.datetime.now()
        with self._db.connection() as conn:
            with conn.cursor() as csr:
                csr.execute((
                    "insert into job_instance ("
                    "flow_instance_id, step_name, status, trigger_actor, "
                    "created_on, updated_on) values ("
                    "%s, %s, %s, %s, %s, %s)"
                ), (flow_instance_id, step_name, JobStatus.STATUS_RUNNING,
                    trigger_actor, now, now))
                conn.commit()
                return JobInstance(
                    id_=csr.lastrowid,
                    flow_instance_id=flow_instance_id,
                    step_name=step_name,
                    status=JobStatus.STATUS_RUNNING,
                    trigger_actor=trigger_actor,
                    created_on=now,
                    updated_on=now
                )
