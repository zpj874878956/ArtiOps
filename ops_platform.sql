-- 首先创建Django认证系统的基础表
-- 创建auth_permission表
-- 需要在auth_permission表之前添加
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 然后修改auth_permission表，添加外键约束
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename` (`content_type_id`,`codename`),
  KEY `auth_permission_content_type_id` (`content_type_id`),
  CONSTRAINT `auth_permission_content_type_id_foreign` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 创建auth_group表
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 创建auth_group_permissions表
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_permission_id` (`permission_id`),
  CONSTRAINT `auth_group_permissions_group_id_foreign` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_group_permissions_permission_id_foreign` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 然后创建用户相关表
-- 创建用户表
CREATE TABLE `users_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `user_type` varchar(20) NOT NULL,
  `phone` varchar(11) DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  `position` varchar(50) DEFAULT NULL,
  `avatar` varchar(100) DEFAULT NULL,
  `last_login_ip` char(39) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 创建用户组关联表
CREATE TABLE `users_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_groups_user_id_group_id` (`user_id`,`group_id`),
  KEY `users_user_groups_group_id` (`group_id`),
  CONSTRAINT `users_user_groups_group_id_foreign` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_user_groups_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 创建用户权限关联表
CREATE TABLE `users_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_user_permissions_user_id_permission_id` (`user_id`,`permission_id`),
  KEY `users_user_user_permissions_permission_id` (`permission_id`),
  CONSTRAINT `users_user_user_permissions_permission_id_foreign` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_user_permissions_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 创建用户登录日志表
CREATE TABLE `users_userloginlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `login_time` datetime(6) NOT NULL,
  `login_ip` char(39) DEFAULT NULL,
  `login_type` varchar(20) NOT NULL,
  `user_agent` longtext,
  `is_success` tinyint(1) NOT NULL,
  `fail_reason` varchar(100) DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `users_userloginlog_user_id` (`user_id`),
  KEY `users_userloginlog_login_time` (`login_time`),
  CONSTRAINT `users_userloginlog_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- =================== 导航栏 ===================
CREATE TABLE `navigation_systemcategory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL COMMENT '分类名称',
  `description` longtext NULL COMMENT '分类描述',
  `icon` varchar(50) NULL COMMENT '图标名称或CSS类',
  `order` int NOT NULL DEFAULT 0 COMMENT '排序，数字越小排序越靠前',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL COMMENT '更新时间',
  `created_by_id` bigint NOT NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  KEY `navigation_systemcategory_created_by_id` (`created_by_id`),
  CONSTRAINT `navigation_systemcategory_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统分类';

CREATE TABLE `navigation_externalsystem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '系统名称',
  `system_type` varchar(20) NOT NULL COMMENT '系统类型',
  `base_url` varchar(200) NOT NULL COMMENT '系统地址',
  `icon` varchar(50) NULL COMMENT '图标名称或CSS类',
  `description` longtext NULL COMMENT '系统描述',
  `status` varchar(20) NOT NULL DEFAULT 'online' COMMENT '状态',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `auth_type` varchar(20) NOT NULL DEFAULT 'none' COMMENT '认证类型',
  `auth_config` json NOT NULL COMMENT '认证配置',
  `order` int NOT NULL DEFAULT 0 COMMENT '排序，数字越小排序越靠前',
  `access_count` int NOT NULL DEFAULT 0 COMMENT '访问次数',
  `score` float NOT NULL DEFAULT 0.0 COMMENT '排序得分',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL COMMENT '更新时间',
  `category_id` bigint NULL COMMENT '所属分类ID',
  `created_by_id` bigint NOT NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  KEY `navigation_externalsystem_category_id` (`category_id`),
  KEY `navigation_externalsystem_created_by_id` (`created_by_id`),
  CONSTRAINT `navigation_externalsystem_category_id_fk` FOREIGN KEY (`category_id`) REFERENCES `navigation_systemcategory` (`id`) ON DELETE SET NULL,
  CONSTRAINT `navigation_externalsystem_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='外部系统';

CREATE TABLE `navigation_systempermission` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `can_access` tinyint(1) NOT NULL DEFAULT 1 COMMENT '允许访问',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `system_id` bigint NOT NULL COMMENT '系统ID',
  `user_id` bigint NULL COMMENT '用户ID',
  `group_id` int NULL COMMENT '用户组ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `navigation_systempermission_system_id_user_id` (`system_id`, `user_id`),
  UNIQUE KEY `navigation_systempermission_system_id_group_id` (`system_id`, `group_id`),
  KEY `navigation_systempermission_system_id` (`system_id`),
  KEY `navigation_systempermission_user_id` (`user_id`),
  KEY `navigation_systempermission_group_id` (`group_id`),
  CONSTRAINT `navigation_systempermission_system_id_fk` FOREIGN KEY (`system_id`) REFERENCES `navigation_externalsystem` (`id`) ON DELETE CASCADE,
  CONSTRAINT `navigation_systempermission_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `navigation_systempermission_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统权限';

CREATE TABLE `navigation_userfavorite` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL COMMENT '收藏时间',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `system_id` bigint NOT NULL COMMENT '系统ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `navigation_userfavorite_user_id_system_id` (`user_id`, `system_id`),
  KEY `navigation_userfavorite_user_id` (`user_id`),
  KEY `navigation_userfavorite_system_id` (`system_id`),
  CONSTRAINT `navigation_userfavorite_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `navigation_userfavorite_system_id_fk` FOREIGN KEY (`system_id`) REFERENCES `navigation_externalsystem` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏';

CREATE TABLE `navigation_accesslog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `access_time` datetime(6) NOT NULL COMMENT '访问时间',
  `access_ip` char(39) NULL COMMENT '访问IP',
  `user_agent` longtext NULL COMMENT 'User Agent',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `system_id` bigint NOT NULL COMMENT '系统ID',
  PRIMARY KEY (`id`),
  KEY `navigation_accesslog_user_id` (`user_id`),
  KEY `navigation_accesslog_system_id` (`system_id`),
  KEY `navigation_accesslog_access_time` (`access_time`),
  CONSTRAINT `navigation_accesslog_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `navigation_accesslog_system_id_fk` FOREIGN KEY (`system_id`) REFERENCES `navigation_externalsystem` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='访问日志';

-- =================== 主机管理 ===================
CREATE TABLE `hosts_hostgroup` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '组名称',
  `description` longtext NULL COMMENT '描述',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL COMMENT '更新时间',
  `created_by_id` bigint NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  KEY `hosts_hostgroup_created_by_id` (`created_by_id`),
  CONSTRAINT `hosts_hostgroup_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='主机组';

CREATE TABLE `hosts_host` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `hostname` varchar(100) NOT NULL COMMENT '主机名',
  `ip_address` varchar(100) NOT NULL COMMENT 'IP地址',
  `port` int NOT NULL DEFAULT 22 COMMENT 'SSH端口',
  `os_type` varchar(50) NULL COMMENT '操作系统类型',
  `os_version` varchar(50) NULL COMMENT '操作系统版本',
  `status` varchar(20) NOT NULL DEFAULT 'unknown' COMMENT '状态',
  `description` longtext NULL COMMENT '描述',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL COMMENT '更新时间',
  `created_by_id` bigint NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hosts_host_hostname_ip_address` (`hostname`, `ip_address`),
  KEY `hosts_host_created_by_id` (`created_by_id`),
  CONSTRAINT `hosts_host_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='主机';

CREATE TABLE `hosts_host_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `host_id` bigint NOT NULL COMMENT '主机ID',
  `hostgroup_id` bigint NOT NULL COMMENT '主机组ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hosts_host_groups_host_id_hostgroup_id` (`host_id`, `hostgroup_id`),
  KEY `hosts_host_groups_host_id` (`host_id`),
  KEY `hosts_host_groups_hostgroup_id` (`hostgroup_id`),
  CONSTRAINT `hosts_host_groups_host_id_fk` FOREIGN KEY (`host_id`) REFERENCES `hosts_host` (`id`) ON DELETE CASCADE,
  CONSTRAINT `hosts_host_groups_hostgroup_id_fk` FOREIGN KEY (`hostgroup_id`) REFERENCES `hosts_hostgroup` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='主机与主机组关联';

CREATE TABLE `hosts_hosttag` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL COMMENT '标签名',
  `color` varchar(20) NOT NULL DEFAULT '#1890ff' COMMENT '标签颜色',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `created_by_id` bigint NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hosts_hosttag_name` (`name`),
  KEY `hosts_hosttag_created_by_id` (`created_by_id`),
  CONSTRAINT `hosts_hosttag_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='主机标签';

CREATE TABLE `hosts_hosttag_hosts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `hosttag_id` bigint NOT NULL COMMENT '标签ID',
  `host_id` bigint NOT NULL COMMENT '主机ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hosts_hosttag_hosts_hosttag_id_host_id` (`hosttag_id`, `host_id`),
  KEY `hosts_hosttag_hosts_hosttag_id` (`hosttag_id`),
  KEY `hosts_hosttag_hosts_host_id` (`host_id`),
  CONSTRAINT `hosts_hosttag_hosts_hosttag_id_fk` FOREIGN KEY (`hosttag_id`) REFERENCES `hosts_hosttag` (`id`) ON DELETE CASCADE,
  CONSTRAINT `hosts_hosttag_hosts_host_id_fk` FOREIGN KEY (`host_id`) REFERENCES `hosts_host` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='主机标签与主机关联';

CREATE TABLE `hosts_sshcredential` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '凭证名称',
  `auth_type` varchar(20) NOT NULL DEFAULT 'password' COMMENT '认证类型',
  `username` varchar(100) NOT NULL COMMENT '用户名',
  `password` varchar(255) NULL COMMENT '密码',
  `private_key` longtext NULL COMMENT '私钥',
  `passphrase` varchar(255) NULL COMMENT '密钥口令',
  `is_default` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否默认',
  `description` longtext NULL COMMENT '描述',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL COMMENT '更新时间',
  `created_by_id` bigint NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  KEY `hosts_sshcredential_created_by_id` (`created_by_id`),
  CONSTRAINT `hosts_sshcredential_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='SSH凭证';

CREATE TABLE `hosts_sshcredential_hosts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sshcredential_id` bigint NOT NULL COMMENT '凭证ID',
  `host_id` bigint NOT NULL COMMENT '主机ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hosts_sshcredential_hosts_sshcredential_id_host_id` (`sshcredential_id`, `host_id`),
  KEY `hosts_sshcredential_hosts_sshcredential_id` (`sshcredential_id`),
  KEY `hosts_sshcredential_hosts_host_id` (`host_id`),
  CONSTRAINT `hosts_sshcredential_hosts_sshcredential_id_fk` FOREIGN KEY (`sshcredential_id`) REFERENCES `hosts_sshcredential` (`id`) ON DELETE CASCADE,
  CONSTRAINT `hosts_sshcredential_hosts_host_id_fk` FOREIGN KEY (`host_id`) REFERENCES `hosts_host` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='SSH凭证与主机关联';

-- =================== 命令管理 ===================
CREATE TABLE `commands_commandtemplate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '模板名称',
  `template_type` varchar(20) NOT NULL COMMENT '模板类型',
  `content` longtext NOT NULL COMMENT '模板内容',
  `description` longtext NULL COMMENT '模板描述',
  `is_public` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否公开',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL COMMENT '更新时间',
  `created_by_id` bigint NOT NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  KEY `commands_commandtemplate_created_by_id` (`created_by_id`),
  CONSTRAINT `commands_commandtemplate_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='命令模板';

CREATE TABLE `commands_commandexecution` (
  `id` varchar(36) NOT NULL COMMENT 'UUID',
  `name` varchar(100) NOT NULL COMMENT '任务名称',
  `execution_type` varchar(20) NOT NULL COMMENT '执行类型',
  `command_content` longtext NOT NULL COMMENT '命令内容',
  `target_hosts` json NOT NULL COMMENT '目标主机',
  `parameters` json NOT NULL COMMENT '执行参数',
  `result` json NULL COMMENT '执行结果',
  `status` varchar(20) NOT NULL DEFAULT 'pending' COMMENT '执行状态',
  `start_time` datetime(6) NULL COMMENT '开始时间',
  `end_time` datetime(6) NULL COMMENT '结束时间',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `created_by_id` bigint NOT NULL COMMENT '执行人ID',
  `template_id` bigint NULL COMMENT '关联模板ID',
  PRIMARY KEY (`id`),
  KEY `commands_commandexecution_created_by_id` (`created_by_id`),
  KEY `commands_commandexecution_template_id` (`template_id`),
  KEY `commands_commandexecution_created_at` (`created_at`),
  CONSTRAINT `commands_commandexecution_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `commands_commandexecution_template_id_fk` FOREIGN KEY (`template_id`) REFERENCES `commands_commandtemplate` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='命令执行记录';

CREATE TABLE `commands_executionlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `host` varchar(100) NULL COMMENT '主机',
  `log_level` varchar(10) NOT NULL DEFAULT 'info' COMMENT '日志级别',
  `message` longtext NOT NULL COMMENT '日志内容',
  `timestamp` datetime(6) NOT NULL COMMENT '记录时间',
  `execution_id` varchar(36) NOT NULL COMMENT '执行记录ID',
  PRIMARY KEY (`id`),
  KEY `commands_executionlog_execution_id` (`execution_id`),
  KEY `commands_executionlog_timestamp` (`timestamp`),
  CONSTRAINT `commands_executionlog_execution_id_fk` FOREIGN KEY (`execution_id`) REFERENCES `commands_commandexecution` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行日志';

CREATE TABLE `commands_dangerouscommand` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `pattern` varchar(200) NOT NULL COMMENT '命令模式',
  `command_type` varchar(10) NOT NULL DEFAULT 'regex' COMMENT '匹配类型',
  `description` longtext NULL COMMENT '危险说明',
  `action` varchar(20) NOT NULL DEFAULT 'warn' COMMENT '处理动作',
  `created_at` datetime(6) NOT NULL COMMENT '创建时间',
  `created_by_id` bigint NOT NULL COMMENT '创建人ID',
  PRIMARY KEY (`id`),
  KEY `commands_dangerouscommand_created_by_id` (`created_by_id`),
  CONSTRAINT `commands_dangerouscommand_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='危险命令';


-- 在文件末尾添加以下Django系统表

-- Django会话表
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Django管理员日志表
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id` (`user_id`),
  KEY `django_admin_log_action_time` (`action_time`),
  CONSTRAINT `django_admin_log_content_type_id_foreign` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Django迁移记录表
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- OAuth2相关表（如果使用OAuth2认证）
CREATE TABLE `oauth2_provider_application` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `client_id` varchar(100) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  `client_secret` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `client_type` varchar(32) NOT NULL,
  `authorization_grant_type` varchar(32) NOT NULL,
  `skip_authorization` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `client_id` (`client_id`),
  KEY `oauth2_provider_application_user_id` (`user_id`),
  CONSTRAINT `oauth2_provider_application_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `oauth2_provider_accesstoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` varchar(255) NOT NULL,
  `expires` datetime(6) NOT NULL,
  `scope` longtext NOT NULL,
  `application_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `source_refresh_token_id` bigint DEFAULT NULL,
  `id_token_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `oauth2_provider_accesstoken_application_id` (`application_id`),
  KEY `oauth2_provider_accesstoken_user_id` (`user_id`),
  KEY `oauth2_provider_accesstoken_source_refresh_token_id` (`source_refresh_token_id`),
  KEY `oauth2_provider_accesstoken_id_token_id` (`id_token_id`),
  CONSTRAINT `oauth2_provider_accesstoken_application_id_foreign` FOREIGN KEY (`application_id`) REFERENCES `oauth2_provider_application` (`id`),
  CONSTRAINT `oauth2_provider_accesstoken_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `oauth2_provider_refreshtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` varchar(255) NOT NULL,
  `access_token_id` bigint NOT NULL,
  `application_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `revoked` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `access_token_id` (`access_token_id`),
  UNIQUE KEY `oauth2_provider_refreshtoken_token` (`token`),
  KEY `oauth2_provider_refreshtoken_application_id` (`application_id`),
  KEY `oauth2_provider_refreshtoken_user_id` (`user_id`),
  CONSTRAINT `oauth2_provider_refreshtoken_access_token_id_foreign` FOREIGN KEY (`access_token_id`) REFERENCES `oauth2_provider_accesstoken` (`id`),
  CONSTRAINT `oauth2_provider_refreshtoken_application_id_foreign` FOREIGN KEY (`application_id`) REFERENCES `oauth2_provider_application` (`id`),
  CONSTRAINT `oauth2_provider_refreshtoken_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;