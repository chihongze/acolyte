DROP TABLE IF EXISTS `job_instance`;
CREATE TABLE `job_instance` (
  id int primary key auto_increment comment "记录ID",
  flow_instance_id int not null comment "flow标识",
  status varchar(20) not null comment "执行状态",
  created_on datetime not null comment "创建时间",
  updated_on datetime not null comment "更新时间"
) engine=InnoDB, default charset utf8;
