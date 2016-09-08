import ujson
from easemob_flow.util.lang import to_str


class Result:

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
        self._status_code = status_code
        self._reason = reason
        self._msg = msg
        self._data = data

    @property
    def status_code(self):
        return self._status_code

    @property
    def reason(self):
        return self._reason

    @property
    def msg(self):
        return self._msg

    @property
    def data(self):
        return self._data

    def __repr__(self):
        return to_str(self, "status_code", "reason", "msg",
                      ("data", ujson.dumps))

    def __str__(self):
        return self.__repr__()
