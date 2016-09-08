DROP TABLE IF EXISTS `flow_instance`;
CREATE TABLE `flow_instance` (
  id int primary key auto_increment comment "运行实例ID",
  flow_template_id int not null comment "隶属的flow_template",
  initiator int not null comment "flow发起人",
  current_step varchar(32) not null comment "当前执行到的step",
  status varchar(32) not null comment "flow执行状态",
  description varchar(1000) not null comment "flow描述",
  created_on datetime not null comment "flow instance创建时间",
  updated_on datetime not null comment "最近更新时间"
) engine=InnoDB, default charset utf8;
