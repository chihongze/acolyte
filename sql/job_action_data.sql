DROP TABLE IF EXISTS `job_action_data`;
CREATE TABLE `job_action_data` (
  id int primary key auto_increment comment "记录ID",
  job_instance_id int not null comment "Job运行实例ID",
  action varchar(255) not null comment "执行步骤",
  actor int not null comment "执行人",
  request_args text not null comment "请求参数",
  response_result text not null comment "",
) engine=InnoDB, default charset utf8;
