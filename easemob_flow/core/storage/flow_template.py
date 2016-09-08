import ujson
from easemob_flow.util import db
from easemob_flow.core.flow import FlowTemplate


def _mapper(result):
    return FlowTemplate(
        id_=result["id"],
        flow_meta=result["flow_meta"],
        name=result["name"],
        bind_args=ujson.loads(result["bind_args"]),
        max_run_instance=result["max_run_instance"],
        creator=result["creator"],
        created_on=result["created_on"]
    )


def query_flow_template_by_id(template_id):
    return db.pool.query_one((
        "select * from flow_template where id = ?"
    ), (template_id,), _mapper)
