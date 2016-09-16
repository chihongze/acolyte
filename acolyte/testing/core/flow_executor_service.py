from acolyte.testing import EasemobFlowTestCase
from acolyte.core.storage.flow_template import FlowTemplateDAO
from acolyte.core.storage.flow_instance import FlowInstanceDAO
from acolyte.core.storage.job_instance import JobInstanceDAO
from acolyte.core.storage.job_action_data import JobActionDataDAO


class FlowExecutorServiceTestCase(EasemobFlowTestCase):

    def setUp(self):
        self._db = self._("db")
        self._flow_exec = self._("FlowExecutorService")
        self._flow_service = self._("FlowService")
        self._flow_tpl_dao = FlowTemplateDAO(self._db)
        self._flow_instance_dao = FlowInstanceDAO(self._db)
        self._job_instance_dao = JobInstanceDAO(self._db)
        self._job_action_data_dao = JobActionDataDAO(self._db)

        self._flow_tpl_id_collector = []
        self._flow_instance_id_collector = []

        # 创建一个flow template供测试使用
        bind_args = {
            "echo": {
                "trigger": {
                    "b": 2
                },
                "multiply": {
                    "c": 3
                },
                "minus": {
                    "d": 11,
                    "e": 12
                }
            }
        }
        rs = self._flow_service.create_flow_template(
            flow_meta_name="test_flow",
            name="sam_test",
            bind_args=bind_args,
            max_run_instance=1,
            creator=1
        )
        self._tpl_id = rs.data.id

        self._flow_tpl_id_collector.append(self._tpl_id)

    def testStartFlow(self):
        """测试启动flow实例
        """

        # 正常启动的情况
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": 5, "y": 6}
        )
        self.assertResultSuccess(rs)
        self.assertTrue(rs.data.id > 0)
        self._flow_instance_id_collector.append(rs.data.id)

        # 使用一个不存在的tpl
        rs = self._flow_exec.start_flow(
            flow_template_id=100086,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": 5, "y": 6}
        )
        self.assertResultBadRequest(rs, "invalid_flow_template")

        # 不合法的initiator
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=100086,
            description="测试flow instance",
            start_flow_args={"x": 5, "y": 6}
        )
        self.assertResultBadRequest(rs, "invalid_initiator")

        # 不合法的start参数
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": "aaaa", "y": 6}
        )
        self.assertResultBadRequest(rs, "start.x_invalid_type")

        # 同时运行多个实例
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": "5", "y": 6}
        )
        self.assertResultBadRequest(rs, "too_many_instance")

    def testHandleJobActions(self):
        """测试Job Action的处理流程
        """

        # 创建一个Flow Instance先
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": 5, "y": 6}
        )

        flow_instance = rs.data
        self._flow_instance_id_collector.append(flow_instance.id)

        # 执行一个不该执行的job step
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="old_man",
            target_action="trigger",
            actor=1,
            action_args={
                "c": 5
            }
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "invalid_target_step")

        # 未trigger先执行一个action
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="multiply",
            actor=1,
            action_args={
                "c": 5
            }
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "no_trigger")

        # 测试正常执行trigger
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="trigger",
            actor=1,
            action_args={}
        )
        self.print_json(rs)
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data, 7)

        # 重复执行相同的action
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="trigger",
            actor=1,
            action_args={}
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "action_already_runned")

        # actor不合法
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="multiply",
            actor=100086,
            action_args={
                "c": 5
            }
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "invalid_actor")

        # 不合法的step name
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="eeeeeee",
            target_action="multiply",
            actor=1,
            action_args={
                "c": 5
            }
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "unknown_target_step")

        # 不合法的action name
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="xxxxxxx",
            actor=1,
            action_args={
                "c": 5
            }
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "unknown_action_handler")

        # 传入错误的flow_instance_id
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=9999999,
            target_step="echo",
            target_action="multiply",
            actor=1,
            action_args={
                "c": 5
            }
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "invalid_flow_instance")

        # 当前step未完成，直接执行下一个
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="old_man",
            target_action="trigger",
            actor=1,
            action_args={}
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "current_step_unfinished")

        # 继续执行multiply action
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="multiply",
            actor=1,
            action_args={
                "c": 2
            }
        )
        self.print_json(rs)
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data, 14)

        # 执行minus action，该action将执行finish
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="minus",
            actor=1,
            action_args={
                "d": 1,
                "e": 2
            }
        )
        self.print_json(rs)
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data, 11)

        # echo step被finish之后再重新执行一次
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="trigger",
            actor=1,
            action_args={}
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "step_already_runned")

        # 执行下一个step - old man
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="old_man",
            target_action="trigger",
            actor=1,
            action_args={}
        )
        self.print_json(rs)
        self.assertResultSuccess(rs)

        # 执行下一个action，返回bad request result
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="old_man",
            target_action="question",
            actor=1,
            action_args={
                "question": "是不是钦定"
            }
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "old_man_angry")

        # 再来一次，这次返回ok result
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="old_man",
            target_action="question",
            actor=1,
            action_args={
                "question": "董先森连任好不好啊"
            }
        )
        self.print_json(rs)
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data, "吼啊")

        # 执行下一个step, 该step完成时会触发flow_meta的on_finish方法
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="job_A",
            target_action="trigger",
            actor=1,
            action_args={
                "x": 1,
                "y": 2
            }
        )
        self.print_json(rs)
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data, 3)

        # 在已经标记为finished的flow_instance上执行
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="trigger",
            actor=1,
            action_args={}
        )
        self.print_json(rs)
        self.assertResultBadRequest(rs, "invalid_status")

        # 重新走一遍，测试中途stop的情况
        rs = self._flow_exec.start_flow(
            flow_template_id=self._tpl_id,
            initiator=1,
            description="测试flow instance",
            start_flow_args={"x": 5, "y": 6}
        )
        flow_instance = rs.data
        self._flow_instance_id_collector.append(flow_instance.id)

        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="trigger",
            actor=1,
            action_args={}
        )
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data, 7)

        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="multiply",
            actor=1,
            action_args={
                "c": 5
            }
        )
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data, 35)

        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="echo",
            target_action="minus",
            actor=1,
            action_args={
                "d": 1,
                "e": 2
            }
        )
        self.assertResultSuccess(rs)
        self.assertEqual(rs.data, 32)

        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="old_man",
            target_action="trigger",
            actor=1,
            action_args={}
        )
        self.assertResultSuccess(rs)

        # 好! 执行angry action会stop整个flow
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="old_man",
            target_action="angry",
            actor=1,
            action_args={}
        )
        self.assertResultBadRequest(rs, "old_man_angry")

        # stop flow之后再去执行某个步骤
        rs = self._flow_exec.handle_job_action(
            flow_instance_id=flow_instance.id,
            target_step="job_A",
            target_action="trigger",
            actor=1,
            action_args={
                "x": 1,
                "y": 2
            }
        )
        self.assertResultBadRequest(rs, "invalid_status")

    def tearDown(self):
        # 各种清数据
        if self._flow_tpl_id_collector:
            self._flow_tpl_dao.delete_by_id(self._flow_tpl_id_collector)
        if self._flow_instance_id_collector:
            self._flow_instance_dao.delete_by_instance_id(
                self._flow_instance_id_collector)
            for flow_instance_id in self._flow_instance_id_collector:
                job_instance_lst = self._job_instance_dao.\
                    query_by_flow_instance_id(flow_instance_id)
                self._job_instance_dao.delete_by_flow_instance_id(
                    flow_instance_id)
                for job_instance in job_instance_lst:
                    self._job_action_data_dao.delete_by_job_instance_id(
                        job_instance.id)
