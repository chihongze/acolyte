import simplejson
import datetime
from acolyte.util.time import common_fmt_dt
from acolyte.core.service import ViewObject


def _default(obj):
    if isinstance(obj, ViewObject) and hasattr(obj, "_to_dict"):
        return obj._to_dict
    if isinstance(obj, datetime.datetime):
        return common_fmt_dt(obj)

    return obj.__dict__


def to_json(obj, sort_keys=False, indent=None, ensure_ascii=False):
    return simplejson.dumps(obj, default=_default,
                            sort_keys=sort_keys, indent=indent,
                            ensure_ascii=ensure_ascii)
