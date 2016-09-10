import simplejson as json
from easemob_flow.core.flow import FlowTemplate
from easemob_flow.core.storage import AbstractDAO


def _mapper(result):
    return FlowTemplate(
        id_=result["id"],
        flow_meta=result["flow_meta"],
        name=result["name"],
        bind_args=json.loads(result["bind_args"]),
        max_run_instance=result["max_run_instance"],
        creator=result["creator"],
        created_on=result["created_on"]
    )


class FlowTemplateDAO(AbstractDAO):

    """针对flow_template表的操作
    """

    def __init__(self, db):
        super().__init__(db)

    def query_flow_template_by_id(self, template_id):
        global _mapper
        return self._db.query_one((
            "select * from flow_template where id = ?"
        ), (template_id,), _mapper)

    def insert_flow_template(self, flow_meta, name, bind_args,
                             max_run_instance, creator, created_on):
        with self._db.connection() as conn:
            with conn.cursor() as csr:
                csr.execute((
                    "insert into `flow_template` "
                    "(flow_meta, name, bind_args, max_run_instance, "
                    "creator, created_on) values ("
                    "?, ?, ?, ?, ?, ?)"
                ), (flow_meta, name, bind_args, max_run_instance,
                    creator, created_on))
                conn.commit()
                return csr.lastrowid

    def is_name_existed(self, name):
        return self._db.execute((
            "select id from flow_template where name = ? limit 1"
        ), (name,))
