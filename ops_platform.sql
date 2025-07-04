-- 首先创建Django认证系统的基础表
-- 创建auth_permission表
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename` (`content_type_id`,`codename`)
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


-------------------导航栏
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
