"""本模块包含跟flow相关的facade接口
"""


def get_all_flow_meta():
    """获得所有的flow_meta信息
    """
    pass


def get_flow_meta_info(flow_meta):
    """获取单个的flow_meta详情
    """
    pass


def create_flow_template(flow_meta, bind_args, creator):
    """创建flow_template
    """
    pass


def get_all_flow_templates():
    """获取所有的flow_templates列表
    """
    pass


def get_flow_template(flow_template_id):
    """获取单个的flow_template详情
    """
    pass


def get_flow_instance_by_status(status, offsert_id, limit, order):
    """根据当前的状态获取flow instance列表
    """
    pass


def get_flow_instance_by_template(template_id, offet_id, limit, order):
    """依据flow_template来查询flow实例
    """
    pass


def get_flow_instance_by_template_and_status(template_id, status,
                                             offset_id, limit, order):
    """依据flow_template和status来查询flow实例
    """
    pass


def get_flow_instance(flow_instance_id):
    """根据id获取flow实例
    """
    pass
