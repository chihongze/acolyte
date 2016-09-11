DROP TABLE IF EXISTS `user_token`;
create table user_token(
  id int primary key comment "用户ID",
  token char(40) not null comment "token",
  session_data varchar(1000) not null comment "会话数据",
  created_on datetime not null comment "创建时间"
) engine=memory, default charset utf8;