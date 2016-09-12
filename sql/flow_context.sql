DROP TABLE IF EXISTS `flow_context`;
create table `flow_context` (
  id int primary key auto_increment,
  flow_instance_id int not null comment "flow instance id",
  k varchar(255) not null,
  v varchar(1000) not null,
  unique key(flow_instance_id, k)
) engine=InnoDB, default charset utf8;
