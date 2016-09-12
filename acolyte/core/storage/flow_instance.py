from acolyte.core.storage import AbstractDAO


class FlowInstanceDAO(AbstractDAO):

    def __init__(self, db):
        super().__init__(db)

    def query_instance_num_by_tpl_id(self, tpl_id):
        return int(self._db.query_one_field((
            "select count(*) as c from flow_instance "
            "where flow_template_id = %s"
        ), (tpl_id,)))
