from abc import ABCMeta


class AbstractService(metaclass=ABCMeta):

    def __init__(self, service_container):
        self._service_container = service_container

    @property
    def container(self):
        return self._service_container

    def _(self, service_id):
        return self.container.get_service(service_id)


class ViewObject(metaclass=ABCMeta):

    """ViewObject用做最终输出的视图对象，可以直接序列化为json
    """
    pass


class Result(ViewObject):

    """该对象用来统一接口返回结果
    """

    # status code list

    STATUS_SUCCESS = 200

    STATUS_BADREQUEST = 400

    STATUS_FORBIDDEN = 403

    STATUS_NOT_FOUND = 404

    STATUS_SERVICE_ERROR = 500

    @classmethod
    def ok(cls, data=None):
        return cls(Result.STATUS_SUCCESS, None, None, data)

    @classmethod
    def bad_request(cls, reason, msg=None, data=None):
        return cls(Result.STATUS_BADREQUEST, reason, msg, data)

    @classmethod
    def not_allow_access(cls, reason, msg=None, data=None):
        return cls(Result.STATUS_FORBIDDEN, reason, msg, data)

    @classmethod
    def service_error(cls, reason, msg=None, data=None):
        return cls(Result.STATUS_SERVICE_ERROR, reason, msg, data)

    def __init__(self, status_code, reason, msg, data):
        """
        :param status_code: 状态码
        :param reason: 如果出现错误，该属性描述一个大致的错误原因
        :param msg: 错误信息
        :param data: 携带数据
        """
        self.status_code = status_code
        self.reason = reason
        self.msg = msg
        self.data = data

    def is_success(self):
        return self._status == Result.STATUS_SUCCESS
