DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  id int primary key auto_increment comment "用户ID",
  email varchar(255) unique not null comment "邮箱",
  name varchar(20) not null comment "姓名",
  role int not null comment "角色",
  created_on datetime not null comment "创建时间",
  last_login_time datetime not null comment "最后登录时间"
) engine=InnoDB, default charset utf8;
