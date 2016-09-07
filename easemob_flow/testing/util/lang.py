import re
import datetime
from easemob_flow.testing import EasemobFlowTestCase
from easemob_flow.util import lang, time


PATTERN = re.compile("<(.*)>")


class DictClass:

    def __init__(self, id_, name, birth, grade):
        self.id_ = id_
        self.name = name
        self.birth = birth
        self.grade = grade


class SlotsClass:

    __slots__ = "id_", "name", "birth"

    def __init__(self, id_, name, birth):
        self.id_ = id_
        self.name = name
        self.birth = birth


class ToStrTestCase(EasemobFlowTestCase):

    """测试lang.to_str函数
    """

    def setUp(self):
        self._dict_obj = DictClass(1, "SamChi", "1989-11-07", 2)
        self._slots_obj = SlotsClass(1, "Jackson", "1989-11-07")

    def testToStringWithTargetFields(self):
        """lang.to_str 指定fields的情形
        """
        string = lang.to_str(self._dict_obj, "name", "birth", "grade")
        self._check_parts_num(string, 3)
        string = lang.to_str(self._slots_obj, "name", "birth")
        self._check_parts_num(string, 2)

    def testToStringWithoutTargetFields(self):
        """lang.to_str 不指定fields的情形
        """
        string = lang.to_str(self._dict_obj)
        self._check_parts_num(string, 4)
        string = lang.to_str(self._slots_obj)
        self._check_parts_num(string, 3)

    def testWithCallback(self):
        """lang.to_str field中包含callback的情况
        """
        dict_obj = DictClass(1, "SamChi", datetime.datetime.now(), 2)
        string = lang.to_str(dict_obj,
                             "name", ("birth", time.common_fmt_dt), "grade")
        print(string)

    def _check_parts_num(self, string, expected_num):
        parts = PATTERN.search(string).group(1).split(',')
        self.assertEqual(len(parts), expected_num)
