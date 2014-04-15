CREATE DATABASE bitshift DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `bitshift`;

CREATE TABLE codelets (
    `codelet_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    `codelet_name` VARCHAR(512) NOT NULL,
    `codelet_code_id` BIGINT UNSIGNED NOT NULL,
    `codelet_lang` SMALLINT UNSIGNED DEFAULT NULL,
    `codelet_origin` TINYINT UNSIGNED DEFAULT NULL,
    `codelet_url` VARCHAR(512) NOT NULL,
    `codelet_date_created` DATETIME DEFAULT NULL,
    `codelet_date_modified` DATETIME DEFAULT NULL,
    PRIMARY KEY (`codelet_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE code (
    `code_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    `code_hash` BIGINT NOT NULL,
    `code_code` MEDIUMTEXT NOT NULL,
    PRIMARY KEY (`code_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- separate tables: authors, symbols, caches, search indices
