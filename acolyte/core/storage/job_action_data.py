from acolyte.core.storage import AbstractDAO
from acolyte.core.job import JobActionData


def _mapper(result):
    result["id_"] = result.pop("id")
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
