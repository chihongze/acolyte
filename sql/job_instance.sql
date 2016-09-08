DROP TABLE IF EXISTS `job_instance`;
CREATE TABLE `job_instance` (
  id int primary key auto_increment comment "运行实例编号",
  flow_instance_id int not null comment "隶属的flow instance",
  status varchar(20) not null comment "job的运行状态",
  trigger_actor int not null comment "job触发者",
  created_on datetime not null comment "创建时间",
  updated_on datetime not null comment "最近的状态更新时间"
) engine=InnoDB, default charset utf8;
