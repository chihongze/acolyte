DROP TABLE IF EXISTS `job_action_data`;
CREATE TABLE `job_action_data` (
  id int primary key auto_increment comment "行为实例编号",
  job_instance_id int not null comment "隶属的job实例",
  action varchar(32) not null comment "动作",
  actor int not null comment "该动作执行人",
  arguments text not null comment "执行该action所需的参数",
  data text not null comment "执行该动作后回填的数据",
  created_on datetime not null comment "开始执行时间",
  finished_on datetime not null comment "结束时间"
) engine=InnoDB, default charset utf8;d
