import simplejson as json
from acolyte.core.flow import FlowTemplate
from acolyte.core.storage import AbstractDAO


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
            "select * from flow_template where id = %s"
        ), (template_id,), _mapper)

    def insert_flow_template(self, flow_meta, name, bind_args,
                             max_run_instance, creator, created_on):
        with self._db.connection() as conn:
            with conn.cursor() as csr:
                csr.execute((
                    "insert into `flow_template` "
                    "(flow_meta, name, bind_args, max_run_instance, "
                    "creator, created_on) values ("
                    "%s, %s, %s, %s, %s, %s)"
                ), (flow_meta, name, bind_args, max_run_instance,
                    creator, created_on))
                conn.commit()
                return FlowTemplate(
                    id_=csr.lastrowid,
                    flow_meta=flow_meta,
                    name=name,
                    bind_args=bind_args,
                    max_run_instance=max_run_instance,
                    creator=creator,
                    created_on=created_on
                )

    def is_name_existed(self, name):
        return self._db.execute((
            "select id from flow_template where name = %s limit 1"
        ), (name,))

    def delete_by_id(self, tpl_id):
        if isinstance(tpl_id, list):
            holders = ",".join(("%s", ) * len(tpl_id))
            return self._db.execute((
                "delete from flow_template where id in ({holders})"
            ).format(holders=holders), (tpl_id,))
        else:
            return self._db.execute((
                "delete from flow_template where id = %s"
            ), (tpl_id,))

    def query_all_templates(self):
        return self._db.query_all((
            "select * from flow_template"
        ), tuple(), _mapper)
