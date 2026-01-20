CREATE TABLE IF NOT EXISTS `users` (
  `user_id` VARCHAR(255) NOT NULL,
  `username` VARCHAR(100),
  `email` VARCHAR(320),
  `full_name` VARCHAR(200),
  `bio` TEXT,
  `account_type` ENUM('personal', 'organization') NOT NULL,
  `plan_type` ENUM('free', 'premium'),
  `status` ENUM('active', 'suspended', 'deleted'),
  `two_factor_enabled` BOOLEAN,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `access_tokens` (
  `token_id` VARCHAR(255) NOT NULL,
  `user_id` VARCHAR(255) NOT NULL,
  `token_name` VARCHAR(255) NOT NULL,
  `token_encoded` VARCHAR(255) NOT NULL,
  `last_used_at` TIMESTAMP,
  `expires_at` TIMESTAMP,
  `status` ENUM('active', 'revoked', 'expired') NOT NULL,
  `created_at` TIMESTAMP,
  PRIMARY KEY (`token_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `organizations` (
  `organization_id` VARCHAR(255) NOT NULL,
  `organization_name` VARCHAR(100),
  `visibility` ENUM("public", "limited", "private"),
  `display_name` VARCHAR(200),
  `description` TEXT,
  `plan_type` ENUM('free', 'team', 'enterprise') NOT NULL,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`organization_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `organization_members` (
  `membership_id` VARCHAR(255) NOT NULL,
  `organization_id` VARCHAR(255) NOT NULL,
  `user_id` VARCHAR(255) NOT NULL,
  `role` ENUM('owner', 'member') NOT NULL,
  `status` ENUM('active', 'pending', 'inactive') NOT NULL,
  `joined_at` TIMESTAMP,
  PRIMARY KEY (`membership_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `workspaces` (
  `workspace_id` VARCHAR(255) NOT NULL,
  `workspace_name` VARCHAR(100),
  `owner_id` VARCHAR(255) NOT NULL,
  `description` TEXT,
  `is_forking_allowed` BOOLEAN DEFAULT FALSE,
  `is_private` BOOLEAN,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`workspace_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `workspace_members` (
  `workspace_member_id` VARCHAR(255),
  `workspace_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `roles` ENUM("Admin", "User"),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `projects` (
  `project_id` VARCHAR(255) NOT NULL,
  `workspace_id` VARCHAR(255),
  `organization_id` VARCHAR(255),
  `project_key` VARCHAR(50) NOT NULL,
  `project_name` VARCHAR(255) NOT NULL,
  `status` ENUM("active", "deleted"),
  `description` TEXT,
  `is_private` BOOLEAN,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `project_members` (
  `project_member_id` VARCHAR(255),
  `project_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `roles` ENUM("Build_Administrator", "Contributor", "Project Administrator", "Reader", "Release_Administrator"),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `repositories` (
  `repository_id` VARCHAR(255) NOT NULL,
  `owner_type` ENUM('user', 'organization') NOT NULL,
  `owner_id` VARCHAR(255) NOT NULL,
  `project_id` VARCHAR(255),
  `repository_name` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `visibility` ENUM('public', 'private', 'internal') NOT NULL,
  `default_branch` VARCHAR(100) DEFAULT 'main',
  `is_fork` BOOLEAN,
  `parent_repository_id` VARCHAR(255),
  `is_archived` BOOLEAN,
  `is_template` BOOLEAN,
  `stars_count` INT,
  `forks_count` INT,
  `license_type` ENUM('MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'unlicensed', 'other'),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  `pushed_at` TIMESTAMP,
  PRIMARY KEY (`repository_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `repository_collaborators` (
  `collaborator_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `user_id` VARCHAR(255) NOT NULL,
  `permission_level` ENUM('read', 'write', 'admin') NOT NULL,
  `status` ENUM('active', 'pending', 'removed') NOT NULL,
  `added_at` TIMESTAMP,
  PRIMARY KEY (`collaborator_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `branches` (
  `branch_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `branch_name` VARCHAR(255) NOT NULL,
  `commit_sha` VARCHAR(40) NOT NULL,
  `source_branch` VARCHAR(255),
  `is_default` BOOLEAN,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`branch_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `commits` (
  `commit_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `commit_sha` VARCHAR(40),
  `author_id` VARCHAR(255) NOT NULL,
  `committer_id` VARCHAR(255) NOT NULL,
  `message` TEXT NOT NULL,
  `parent_commit_id` VARCHAR(255),
  `committed_at` TIMESTAMP NOT NULL,
  `created_at` TIMESTAMP,
  PRIMARY KEY (`commit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `directories` (
  `directory_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `branch_id` VARCHAR(255) NOT NULL,
  `directory_path` VARCHAR(1000) NOT NULL,
  `parent_directory_id` VARCHAR(255),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`directory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `files` (
  `file_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `branch_id` VARCHAR(255) NOT NULL,
  `directory_id` VARCHAR(255),
  `file_path` VARCHAR(1000) NOT NULL,
  `file_name` VARCHAR(255) NOT NULL,
  `language` ENUM( 'C', 'C++', 'C#', 'Go', 'Rust', 'Java', 'Kotlin', 'Scala', 'Python', 'Ruby', 'PHP', 'JavaScript', 'TypeScript', 'Shell', 'PowerShell', 'Swift', 'Objective-C', 'Dart', 'R', 'MATLAB', 'Groovy', 'Perl', 'Lua', 'Haskell', 'Elixir', 'Erlang', 'Julia', 'Assembly', 'Fortran', 'COBOL',  'HTML', 'CSS', 'SCSS', 'Less', 'Markdown', 'AsciiDoc',  'JSON', 'YAML', 'XML', 'TOML', 'INI', 'CSV',  'Dockerfile', 'Makefile', 'Bash', 'Terraform', 'Ansible',  'SQL', 'PLpgSQL',  'Text', 'Binary', 'Unknown' ),
  `is_binary` BOOLEAN,
  `last_modified_at` TIMESTAMP NOT NULL,
  `last_commit_id` VARCHAR(255),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`file_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `file_contents` (
  `content_id` VARCHAR(255) NOT NULL,
  `file_id` VARCHAR(255) NOT NULL,
  `commit_id` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `encoding` ENUM('utf-8', 'base64', 'binary') NOT NULL,
  `created_at` TIMESTAMP,
  PRIMARY KEY (`content_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `code_reviews` (
  `code_review_id` VARCHAR(255) NOT NULL,
  `pull_request_id` VARCHAR(255) NOT NULL,
  `file_path` VARCHAR(1000) NOT NULL,
  `reviewer_id` VARCHAR(255) NOT NULL,
  `comment_body` TEXT NOT NULL,
  `review_type` ENUM('comment', 'suggestion', 'question') NOT NULL,
  `status` ENUM('pending', 'resolved', 'outdated') NOT NULL,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`code_review_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `pull_requests` (
  `pull_request_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `pull_request_number` INT NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `description` TEXT,
  `author_id` VARCHAR(255) NOT NULL,
  `source_branch` VARCHAR(255) NOT NULL,
  `target_branch` VARCHAR(255) NOT NULL,
  `status` ENUM('open', 'closed', 'merged', 'draft') NOT NULL,
  `merged_by` VARCHAR(255),
  `merged_at` TIMESTAMP,
  `closed_at` TIMESTAMP,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`pull_request_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `pull_request_reviews` (
  `review_id` VARCHAR(255) NOT NULL,
  `pull_request_id` VARCHAR(255) NOT NULL,
  `reviewer_id` VARCHAR(255) NOT NULL,
  `review_state` ENUM('pending', 'approved', 'changes_requested', 'commented', 'dismissed') NOT NULL,
  `review_body` TEXT,
  `submitted_at` TIMESTAMP,
  `created_at` TIMESTAMP,
  PRIMARY KEY (`review_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `issues` (
  `issue_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `issue_number` INT NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `description` TEXT,
  `author_id` VARCHAR(255) NOT NULL,
  `assignee_id` VARCHAR(255),
  `status` ENUM('open', 'closed', 'in_progress') NOT NULL,
  `priority` ENUM('low', 'medium', 'high', 'critical'),
  `issue_type` ENUM('bug', 'feature', 'documentation', 'question', 'enhancement') NOT NULL,
  `closed_at` TIMESTAMP,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`issue_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `comments` (
  `comment_id` VARCHAR(255) NOT NULL,
  `commentable_type` ENUM('issue', 'pull_request') NOT NULL,
  `commentable_id` VARCHAR(255) NOT NULL,
  `author_id` VARCHAR(255) NOT NULL,
  `comment_body` TEXT NOT NULL,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`comment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `labels` (
  `label_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `label_name` VARCHAR(100) NOT NULL,
  `color` VARCHAR(7) NOT NULL,
  `pr_ids` VARCHAR(255),
  `issue_ids` VARCHAR(255),
  `description` VARCHAR(500),
  `created_at` TIMESTAMP,
  PRIMARY KEY (`label_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `workflows` (
  `workflow_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `workflow_name` VARCHAR(255) NOT NULL,
  `workflow_path` VARCHAR(500) NOT NULL,
  `trigger_event` ENUM('push', 'pull_request', 'schedule', 'workflow_dispatch', 'release') NOT NULL,
  `status` ENUM('active', 'disabled', 'deleted') NOT NULL,
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  PRIMARY KEY (`workflow_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `releases` (
  `release_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `tag_name` VARCHAR(100) NOT NULL,
  `release_name` VARCHAR(255),
  `description` TEXT,
  `author_id` VARCHAR(255) NOT NULL,
  `target_type` ENUM('commit', 'branch'),
  `target_reference` VARCHAR(255),
  `is_draft` BOOLEAN,
  `is_prerelease` BOOLEAN,
  `published_at` TIMESTAMP,
  `created_at` TIMESTAMP,
  PRIMARY KEY (`release_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `notifications` (
  `notification_id` VARCHAR(255) NOT NULL,
  `user_id` VARCHAR(255) NOT NULL,
  `notification_type` ENUM('mention', 'review_request', 'issue_assigned', 'pr_merged', 'ci_failed') NOT NULL,
  `reference_type` ENUM('issue', 'pull_request', 'commit', 'release') NOT NULL,
  `reference_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255),
  `is_read` BOOLEAN,
  `read_at` TIMESTAMP,
  `created_at` TIMESTAMP,
  PRIMARY KEY (`notification_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `stars` (
  `star_id` VARCHAR(255) NOT NULL,
  `user_id` VARCHAR(255) NOT NULL,
  `repository_id` VARCHAR(255) NOT NULL,
  `starred_at` TIMESTAMP,
  PRIMARY KEY (`star_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;