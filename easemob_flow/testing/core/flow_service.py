from easemob_flow.core.service import Result
from easemob_flow.testing import EasemobFlowTestCase
from easemob_flow.core.storage.flow_template import FlowTemplateDAO


class FlowServiceTestCase(EasemobFlowTestCase):

    def setUp(self):
        self.flow_service = self._("FlowService")
        self.flow_meta_mgr = self._("flow_meta_manager")
        self.flow_tpl_dao = FlowTemplateDAO(self._("db"))
        self._flow_tpl_collector = []

    def test_get_all_flow_meta(self):
        """测试获取所有的flow meta对象信息
        """
        result = self.flow_service.get_all_flow_meta()
        self.assertEqual(result.status_code, Result.STATUS_SUCCESS)

    def test_get_flow_meta_info(self):
        """测试获取单个flow_meta对象
        """

        # 测试正常返回的情况
        result = self.flow_service.get_flow_meta_info("test_flow")
        self.assertEqual(result.status_code, Result.STATUS_SUCCESS)

        # 找不到指定的flow meta
        result = self.flow_service.get_flow_meta_info("heheda")
        self.assertEqual(result.status_code, Result.STATUS_BADREQUEST)
        self.assertEqual(result.reason, "flow_meta_not_exist")

    def testValidateTplBindArgs(self):
        """测试验证绑定参数
        """

        flow_meta = self.flow_meta_mgr.get("test_flow")

        # 正常验证通过
        rs = self.flow_service._validate_tpl_bind_args(flow_meta, {
            "echo": {
                "trigger": {
                    "b": 2
                },
                "finish": {
                    "c": 3
                },
                "stop": {
                    "d": "1111",
                    "e": "10"
                },
            }
        })
        self.assertResultSuccess(rs)

        # 测试是否能对参数应用转换
        rs = self.flow_service._validate_tpl_bind_args(flow_meta, {
            "echo": {
                "trigger": {
                    "b": "2",
                },
                "finish": {
                    "c": "3",
                },
                "stop": {
                    "d": 12.34,
                    "e": 12
                }
            }
        })
        self.assertResultSuccess(rs)
        new_flow_meta = rs.data
        self.assertEqual(new_flow_meta["echo"]["trigger"]["b"], 2)
        self.assertEqual(new_flow_meta["echo"]["finish"]["c"], 3)
        self.assertEqual(new_flow_meta["echo"]["stop"]["d"], "12.34")
        self.assertEqual(new_flow_meta["echo"]["stop"]["e"], "12")

        # 测试出错的情况
        rs = self.flow_service._validate_tpl_bind_args(flow_meta, {
            "echo": {
                "trigger": {
                    "b": 2
                },
                "finish": {
                    "c": 3
                },
                "stop": {
                    "d": "1",
                    "e": "10"
                },
            }
        })
        self.assertResultBadRequest(rs, "echo_stop_d_less_than_min_length")

    def testCreateFlowTemplate(self):
        """测试创建flow template
        """

        bind_args = {
            "echo": {
                "trigger": {
                    "b": 2
                },
                "finish": {
                    "c": 3
                },
                "stop": {
                    "d": 12.34,
                    "e": 12
                }
            }
        }

        # 正常创建
        rs = self.flow_service.create_flow_template(
            flow_meta_name="test_flow",
            name="sam_test",
            bind_args=bind_args,
            max_run_instance=1,
            creator=1
        )
        self.assertResultSuccess(rs)
        self._flow_tpl_collector.append(rs.data.id)

        # 创建重名
        rs = self.flow_service.create_flow_template(
            flow_meta_name="test_flow",
            name="sam_test",
            bind_args=bind_args,
            max_run_instance=1,
            creator=1
        )
        self.assertResultBadRequest(rs, "name_already_exist")

        # flow meta不存在
        rs = self.flow_service.create_flow_template(
            flow_meta_name="test_flow_x",
            name="sam_testx",
            bind_args=bind_args,
            max_run_instance=1,
            creator=1
        )
        self.assertResultBadRequest(rs, "flow_meta_not_exist")

        # creator不存在
        rs = self.flow_service.create_flow_template(
            flow_meta_name="test_flow",
            name="sam_test_x",
            bind_args=bind_args,
            max_run_instance=1,
            creator=2
        )
        self.assertResultBadRequest(rs, "invalid_creator_id")

        # bind_args验证出问题
        err_bind_args = {
            "echo": {
                "trigger": {
                    "b": 2
                },
                "finish": {
                    "c": 3
                },
                "stop": {
                    "d": "1",
                    "e": "122342"
                }
            }
        }
        rs = self.flow_service.create_flow_template(
            flow_meta_name="test_flow",
            name="sam_test_x",
            bind_args=err_bind_args,
            max_run_instance=1,
            creator=1
        )
        self.assertResultBadRequest(rs, "echo_stop_d_less_than_min_length")

    def testGetAllFlowTemplates(self):
        rs = self.flow_service.create_flow_template(
            flow_meta_name="test_flow",
            name="sam_test",
            bind_args={
                "echo": {
                    "trigger": {
                        "b": 2
                    },
                    "finish": {
                        "c": 3
                    },
                    "stop": {
                        "d": 12.34,
                        "e": 12
                    }
                }
            },
            max_run_instance=1,
            creator=1
        )
        self._flow_tpl_collector.append(rs.data.id)
        rs = self.flow_service.get_all_flow_templates()
        self.assertResultSuccess(rs)
        self.assertEqual(len(rs.data), 1)

    def tearDown(self):
        if self._flow_tpl_collector:
            self.flow_tpl_dao.delete_by_id(self._flow_tpl_collector)
