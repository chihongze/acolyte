import datetime
from acolyte.core.storage import AbstractDAO
from acolyte.core.flow import FlowInstance, FlowStatus


class FlowInstanceDAO(AbstractDAO):

    def __init__(self, db):
        super().__init__(db)

    def query_instance_num_by_tpl_id(self, tpl_id):
        return int(self._db.query_one_field((
            "select count(*) as c from flow_instance "
            "where flow_template_id = %s"
        ), (tpl_id,)))

    def insert(self, flow_template_id, initiator, description):
        now = datetime.datetime.now()
        with self._db.connection() as conn:
            with conn.cursor() as csr:
                csr.execute((
                    "insert into flow_instance ("
                    "flow_template_id, initiator, current_step, status, "
                    "description, created_on, updated_on) values ("
                    "%s, %s, %s, %s, %s, %s, %s)"
                ), (flow_template_id, initiator, "start",
                    FlowStatus.STATUS_RUNNING, description, now, now))
                conn.commit()
                return FlowInstance(
                    id_=csr.lastrowid,
                    flow_template_id=flow_template_id,
                    initiator=initiator,
                    current_step="start",
                    status=FlowStatus.STATUS_RUNNING,
                    description=description,
                    created_on=now,
                    updated_on=now
                )

    def delete_by_instance_id(self, instance_id):
        if isinstance(instance_id, list):
            holders = ",".join(("%s", ) * len(instance_id))
            return self._db.execute(
                "delete from flow_instance where id in ({holders})".format(
                    holders=holders), instance_id)
        else:
            return self._db.execute("delete from flow_instance where id = %s",
                                    (instance_id, ))
