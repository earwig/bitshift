CREATE DATABASE `bitshift` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `bitshift`;

CREATE TABLE `languages` (
    `language_id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    `language_name` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`language_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `origins` (
    `origin_id` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    `origin_name` VARCHAR(64) NOT NULL,
    `origin_url` VARCHAR(512) NOT NULL,
    `origin_url_base` VARCHAR(512) NOT NULL,
    `origin_image` TINYBLOB DEFAULT NULL, -- TODO: verify size (<64kB)
    PRIMARY KEY (`origin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `codelets` (
    `codelet_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    `codelet_name` VARCHAR(512) NOT NULL,
    `codelet_code_id` BIGINT UNSIGNED NOT NULL,
    `codelet_lang` SMALLINT UNSIGNED DEFAULT NULL, -- TODO: needs index
    `codelet_origin` TINYINT UNSIGNED NOT NULL,
    `codelet_url` VARCHAR(512) NOT NULL,
    `codelet_date_created` DATETIME DEFAULT NULL, -- TODO: needs index
    `codelet_date_modified` DATETIME DEFAULT NULL, -- TODO: needs index
    PRIMARY KEY (`codelet_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `code` (
    `code_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    `code_hash` BIGINT NOT NULL, -- TODO: needs index
    `code_code` MEDIUMTEXT NOT NULL, -- TODO: verify size (16mB?)
    PRIMARY KEY (`code_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `authors` (
    `author_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    `author_codelet` BIGINT UNSIGNED NOT NULL, -- TODO: foreign index?
    `author_name` VARCHAR(128) NOT NULL, -- TODO: needs index
    `author_url` VARCHAR(512) DEFAULT NULL,
    PRIMARY KEY (`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `symbols` (
    `symbol_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
    `symbol_codelet` BIGINT UNSIGNED NOT NULL, -- TODO: foreign index?
    `symbol_type` TINYINT UNSIGNED NOT NULL, -- TODO: multi-column index?
    `symbol_name` VARCHAR(512) NOT NULL, -- TODO: needs index
    `symbol_row` INT UNSIGNED NOT NULL,
    `symbol_col` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`symbol_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `query_cache` (
    `qcache_id` INT NOT NULL UNIQUE,
    `qcache_query` VARCHAR(512) NOT NULL,
    `qcache_results` BLOB NOT NULL, -- TODO: verify; perhaps use some kind of array
    `qcache_page` TINYINT UNSIGNED NOT NULL,
    `qcache_count_mnt` TINYINT UNSIGNED NOT NULL,
    `qcache_count_exp` TINYINT UNSIGNED NOT NULL,
    `qcache_created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- TODO: verify
    `qcache_last_used` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- TODO: verify
    PRIMARY KEY (`cache_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- TODO: full-text search index table
