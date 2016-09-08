from abc import ABCMeta, abstractmethod


class AbstractFlowExecutor(meta=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def start_flow(self, flow_name, start_flow_args, first_job_trigger_args):
        """开启一个flow进程，创建flow_instance并执行第一个Job
           :param flow_name: 具体的flow_template的名称
           :param first_job_trigger_args: 触发第一个Job需要的参数
           :return flow_instance
        """
        pass

    @abstractmethod
    def next_job(self, flow_instance_id, current_job_finish_args,
                 new_job_trigger_args):
        """执行下一个Job
           :param flow_instance_id: flow的标识，可以是flow_template或者flow_instance_id
           :param current_job_finish_args: 用于结束当前Job的参数
           :param new_job_trigger_args: 用于触发新Job的参数
           :return job_instance
        """
        pass

    @abstractmethod
    def handle_job_action(self, flow_instance_id, job_action, action_args):
        """处理Job中的自定义动作
           :param flow_instance_id: flow的标识
           :param job_action: 自定义的动作名称
           :param action_args: 执行该自定义动作所需要的参数
        """
        pass

    @abstractmethod
    def stop(self, flow_instance_id, stop_flow_args, stop_job_args):
        """终止flow
           :param flow_instance_id flow的标识
           :param stop_args 终止参数
        """
        pass