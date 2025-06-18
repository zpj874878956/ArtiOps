CREATE TABLE `system_systemconfig` (
    `id` int NOT NULL AUTO_INCREMENT,
    `key` varchar(100) NOT NULL UNIQUE,
    `value` text NOT NULL,
    `description` text NOT NULL,
    `is_encrypted` boolean NOT NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `credentials_credential` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `credential_type` varchar(20) NOT NULL,
    `description` text NOT NULL,
    `username` varchar(100) NOT NULL,
    `password` text NOT NULL,
    `private_key` text NOT NULL,
    `key_passphrase` text NOT NULL,
    `token` text NOT NULL,
    `extra_data` text NOT NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `expires_at` datetime NULL,
    `created_by_id` int NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `credentials_credentialusagelog` (
    `id` int NOT NULL AUTO_INCREMENT,
    `ip_address` varchar(50) NOT NULL,
    `used_at` datetime NOT NULL,
    `action` varchar(100) NOT NULL,
    `task_info` text NOT NULL,
    `credential_id` int NOT NULL,
    `user_id` int NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `builds_buildtask` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `description` text NOT NULL,
    `command` text NOT NULL,
    `parameters` text NOT NULL,
    `environment_variables` text NOT NULL,
    `status` varchar(20) NOT NULL,
    `is_scheduled` boolean NOT NULL,
    `schedule` varchar(100) NOT NULL,
    `timeout` int NOT NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `created_by_id` int NULL,
    `project_id` int NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `builds_buildhistory` (
    `id` int NOT NULL AUTO_INCREMENT,
    `build_number` int NOT NULL,
    `status` varchar(20) NOT NULL,
    `execution_path` varchar(255) NOT NULL,
    `log_file` varchar(255) NOT NULL,
    `started_at` datetime NOT NULL,
    `finished_at` datetime NULL,
    `duration` int NOT NULL,
    `executed_by_id` int NULL,
    `task_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `builds_buildhistory_task_id_build_number_uniq` (`task_id`, `build_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `logs_loginlog` (
    `id` int NOT NULL AUTO_INCREMENT,
    `username` varchar(150) NOT NULL,
    `ip_address` varchar(50) NOT NULL,
    `user_agent` text NOT NULL,
    `login_time` datetime NOT NULL,
    `status` varchar(20) NOT NULL,
    `message` text NOT NULL,
    `user_id` int NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `logs_operationlog` (
    `id` int NOT NULL AUTO_INCREMENT,
    `username` varchar(150) NOT NULL,
    `ip_address` varchar(50) NOT NULL,
    `operation_time` datetime NOT NULL,
    `action` varchar(20) NOT NULL,
    `resource_type` varchar(20) NOT NULL,
    `resource_id` varchar(50) NOT NULL,
    `resource_name` varchar(255) NOT NULL,
    `content` text NOT NULL,
    `status` varchar(20) NOT NULL,
    `user_id` int NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users_user` (
    `id` int NOT NULL AUTO_INCREMENT,
    `password` varchar(128) NOT NULL,
    `last_login` datetime(6) NULL,
    `is_superuser` boolean NOT NULL,
    `username` varchar(150) NOT NULL UNIQUE,
    `first_name` varchar(150) NOT NULL,
    `last_name` varchar(150) NOT NULL,
    `email` varchar(254) NOT NULL,
    `is_staff` boolean NOT NULL,
    `is_active` boolean NOT NULL,
    `date_joined` datetime(6) NOT NULL,
    `phone` varchar(20) NOT NULL,
    `position` varchar(100) NOT NULL,
    `avatar` varchar(100) NOT NULL,
    `real_name` varchar(150) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users_user_groups` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `group_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `users_user_groups_user_id_group_id_uniq` (`user_id`, `group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users_user_user_permissions` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `permission_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `users_user_user_permissions_user_id_permission_id_uniq` (`user_id`, `permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `projects_project` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `key` varchar(20) NOT NULL,
    `description` text NOT NULL,
    `repository_url` varchar(255) NOT NULL,
    `repository_type` varchar(20) NOT NULL,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `created_by_id` int NULL,
    `owner_id` int NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `projects_projectmember` (
    `id` int NOT NULL AUTO_INCREMENT,
    `role` varchar(20) NOT NULL,
    `joined_at` datetime NOT NULL,
    `project_id` int NOT NULL,
    `user_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `projects_projectmember_project_id_user_id_uniq` (`project_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

