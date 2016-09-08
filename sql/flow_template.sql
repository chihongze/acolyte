DROP TABLE IF EXISTS `flow_template`;
CREATE TABLE `flow_template` (
  id int primary key auto_increment comment "flow template id",
  flow_meta varchar(32) not null comment "所属的flow_meta",
  name varchar(32) not null comment "flow template name",
  bind_args text not null comment "绑定的参数",
  max_run_instance int not null comment "允许的最大运行实例数目",
  creator int not null comment "创建者",
  created_on datetime not null comment "创建时间"
) engine=InnoDB, default charset utf8;
