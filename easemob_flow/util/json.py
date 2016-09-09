import simplejson
from easemob_flow.core.service import ViewObject


def _default(obj):
    if isinstance(obj, ViewObject) and hasattr(obj, "_to_dict"):
        return obj._to_dict
    return obj.__dict__


def to_json(obj, sort_keys=False, indent=None):
    return simplejson.dumps(obj, default=_default,
                            sort_keys=sort_keys, indent=indent)
