-- 修复数据库表结构与Django模型之间的差异
-- 生成日期: 用于ArtiOps项目

-- 1. 添加缺失的表

-- 创建用户角色表 users_role
CREATE TABLE `users_role` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(50) NOT NULL UNIQUE,
    `key` varchar(50) NOT NULL UNIQUE,
    `permissions` JSON NULL,
    `description` text NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建环境表 environments_environment
CREATE TABLE `environments_environment` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `type` varchar(20) NOT NULL,
    `description` text NULL,
    `api_endpoint` varchar(200) NULL,
    `variables` JSON NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `created_by_id` int NULL,
    `project_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `environments_environment_name_project_id_uniq` (`name`, `project_id`),
    FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`project_id`) REFERENCES `projects_project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 修改字段不匹配的表

-- 修改 users_user 表，添加缺失的字段
ALTER TABLE `users_user` 
    ADD COLUMN `role_id` int NULL AFTER `real_name`,
    ADD COLUMN `status` boolean NOT NULL DEFAULT TRUE AFTER `role_id`,
    ADD COLUMN `last_login_ip` varchar(39) NULL AFTER `status`,
    ADD COLUMN `last_login_time` datetime NULL AFTER `last_login_ip`,
    ADD FOREIGN KEY (`role_id`) REFERENCES `users_role` (`id`) ON DELETE SET NULL;

-- 3. 修改现有字段属性，使其与模型定义一致

-- 修改 system_systemconfig 表中的字段
ALTER TABLE `system_systemconfig` 
    MODIFY `description` text NULL;

-- 修改 projects_project 表中的字段
ALTER TABLE `projects_project`
    MODIFY `key` varchar(50) NOT NULL UNIQUE,
    MODIFY `description` text NULL;

-- 如果想要保留repository相关字段，需要修改projects/models.py添加这些字段
-- 如果不需要，可以删除这些字段
-- ALTER TABLE `projects_project`
--     DROP COLUMN `repository_url`,
--     DROP COLUMN `repository_type`;

-- 修改 projects_projectmember 表中的字段
ALTER TABLE `projects_projectmember`
    CHANGE `joined_at` `created_at` datetime NOT NULL,
    MODIFY `role` varchar(50) NOT NULL;

-- 修改 builds_buildtask 表中的JSON字段
ALTER TABLE `builds_buildtask`
    MODIFY `parameters` JSON NULL,
    MODIFY `environment_variables` JSON NULL,
    MODIFY `schedule` varchar(100) NULL;

-- 修改 builds_buildhistory 表中的字段
ALTER TABLE `builds_buildhistory`
    MODIFY `execution_path` varchar(255) NULL,
    MODIFY `log_file` varchar(255) NULL;

-- 修改 credentials_credential 表中的字段
ALTER TABLE `credentials_credential`
    MODIFY `description` text NULL,
    MODIFY `username` varchar(100) NULL,
    MODIFY `password` text NULL,
    MODIFY `private_key` text NULL,
    MODIFY `key_passphrase` text NULL,
    MODIFY `token` text NULL,
    MODIFY `extra_data` JSON NULL;

-- 修改 credentials_credentialusagelog 表中的字段
ALTER TABLE `credentials_credentialusagelog`
    MODIFY `ip_address` varchar(50) NULL,
    MODIFY `action` varchar(100) NULL,
    MODIFY `task_info` JSON NULL;

-- 修改 logs_loginlog 表中的字段
ALTER TABLE `logs_loginlog`
    MODIFY `user_agent` text NULL,
    MODIFY `message` text NULL;

-- 修改 logs_operationlog 表中的字段
ALTER TABLE `logs_operationlog`
    MODIFY `resource_id` varchar(50) NULL,
    MODIFY `resource_name` varchar(255) NULL,
    MODIFY `content` text NULL;

-- 4. 添加必要的索引

-- 为 users_user 表的 role_id 添加索引
CREATE INDEX `users_user_role_id_idx` ON `users_user` (`role_id`);

-- 为 environments_environment 表的外键添加索引
CREATE INDEX `environments_environment_created_by_id_idx` ON `environments_environment` (`created_by_id`);
CREATE INDEX `environments_environment_project_id_idx` ON `environments_environment` (`project_id`);

-- 5. 处理用户表中多余的字段（如果不需要）
-- 注意：删除字段可能导致数据丢失，请确保这些字段中没有重要数据

-- ALTER TABLE `users_user`
--     DROP COLUMN `position`,
--     DROP COLUMN `avatar`; 