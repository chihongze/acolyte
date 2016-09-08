DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  id int primary key auto_increment comment "角色编号",
  name varchar(255) not null comment "角色名称",
  description varchar(1000) not null comment "角色描述"
) engine=InnoDB, default charset utf8;
