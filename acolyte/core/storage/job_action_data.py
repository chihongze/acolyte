import datetime
import simplejson as json
from acolyte.core.storage import AbstractDAO
from acolyte.core.job import JobActionData


def _mapper(result):
    result["id_"] = result.pop("id")
    result["arguments"] = json.loads(result["arguments"])
    result["data"] = json.loads(result["data"])
    return JobActionData(**result)


class JobActionDataDAO(AbstractDAO):

    def __init__(self, db):
        super().__init__(db)

    def query_by_id(self, id_):
        return self._db.query_one((
            "select * from job_action_data "
            "where id = %s"
        ), (id_,), _mapper)

    def query_by_job_instance_id_and_action(self, job_instance_id, action):
        return self._db.query_one((
            "select * from job_action_data where "
            "job_instance_id = %s and action = %s limit 1"
        ), (job_instance_id, action), _mapper)

    def insert(self, job_instance_id, action, actor, arguments, data):
        now = datetime.datetime.now()
        with self._db.connection() as conn:
            with conn.cursor() as csr:
                csr.execute((
                    "insert into job_action_data ("
                    "job_instance_id, action, actor, "
                    "arguments, data, created_on, updated_on)"
                    "values (%s, %s, %s, %s, %s, %s, %s)"
                ), (job_instance_id, action, actor, json.dumps(arguments),
                    json.dumps(data), now, now))
                conn.commit()
                return JobActionData(
                    id_=csr.lastrowid,
                    job_instance_id=job_instance_id,
                    action=action,
                    actor=actor,
                    arguments=arguments,
                    data=data,
                    created_on=now,
                    updated_on=now
                )

    def update_data(self, action_data_id, data):
        now = datetime.datetime.now()
        return self._db.execute((
            "update job_action_data set data = %s, "
            "updated_on = %s "
            "where id = %s"
        ), (json.dumps(data), now, action_data_id))

    def delete_by_id(self, job_action_data_id):
        return self._db.execute((
            "delete from job_action_data where id = %s"
        ), (job_action_data_id))

    def delete_by_job_instance_id(self, job_instance_id):
        return self._db.execute((
            "delete from job_action_data where job_instance_id = %s"
        ), (job_instance_id,))
