-- Schema version 2

CREATE DATABASE `bitshift` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `bitshift`;

CREATE TABLE `version` (
    `version` INT UNSIGNED NOT NULL
) ENGINE=InnoDB;

CREATE TABLE `origins` (
    `origin_id` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `origin_name` VARCHAR(64) NOT NULL,
    `origin_url` VARCHAR(512) NOT NULL,
    `origin_url_base` VARCHAR(512) NOT NULL,
    `origin_image` BLOB DEFAULT NULL,
    PRIMARY KEY (`origin_id`)
) ENGINE=InnoDB;

CREATE TABLE `code` (
    `code_id` BIGINT NOT NULL,
    `code_code` MEDIUMTEXT NOT NULL,
    PRIMARY KEY (`code_id`),
    FULLTEXT KEY (`code_code`)
) ENGINE=InnoDB;

CREATE TABLE `codelets` (
    `codelet_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `codelet_name` VARCHAR(300) NOT NULL,
    `codelet_code_id` BIGINT UNSIGNED NOT NULL,
    `codelet_lang` SMALLINT UNSIGNED DEFAULT NULL,
    `codelet_origin` TINYINT UNSIGNED NOT NULL,
    `codelet_url` VARCHAR(512) NOT NULL,
    `codelet_rank` FLOAT NOT NULL,
    `codelet_date_created` DATETIME DEFAULT NULL,
    `codelet_date_modified` DATETIME DEFAULT NULL,
    PRIMARY KEY (`codelet_id`),
    FULLTEXT KEY (`codelet_name`),
    KEY (`codelet_lang`),
    KEY (`codelet_rank`),
    KEY (`codelet_date_created`),
    KEY (`codelet_date_modified`),
    FOREIGN KEY (`codelet_code_id`)
        REFERENCES `code` (`code_id`)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (`codelet_origin`)
        REFERENCES `origins` (`origin_id`)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `authors` (
    `author_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `author_codelet` BIGINT UNSIGNED NOT NULL,
    `author_name` VARCHAR(128) NOT NULL,
    `author_url` VARCHAR(512) DEFAULT NULL,
    PRIMARY KEY (`author_id`),
    FULLTEXT KEY (`author_name`),
    FOREIGN KEY (`author_codelet`)
        REFERENCES `codelets` (`codelet_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `symbols` (
    `symbol_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `symbol_codelet` BIGINT UNSIGNED NOT NULL,
    `symbol_type` TINYINT UNSIGNED NOT NULL,
    `symbol_name` VARCHAR(512) NOT NULL,
    `symbol_row` INT UNSIGNED NOT NULL,
    `symbol_col` INT UNSIGNED NOT NULL,
    `symbol_end_row` INT UNSIGNED NOT NULL,
    `symbol_end_col` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`symbol_id`),
    KEY (`symbol_type`, `symbol_name`(32)),
    FOREIGN KEY (`symbol_codelet`)
        REFERENCES `codelets` (`codelet_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `cache` (
    `cache_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `cache_hash` BIGINT NOT NULL,
    `cache_count_mnt` TINYINT UNSIGNED NOT NULL,
    `cache_count_exp` TINYINT UNSIGNED NOT NULL,
    `cache_created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `cache_last_used` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`cache_id`)
) ENGINE=InnoDB;

CREATE TABLE `cache_data` (
    `cdata_cache` INT UNSIGNED NOT NULL,
    `cdata_codelet` BIGINT UNSIGNED NOT NULL,
    FOREIGN KEY (`cdata_cache`)
        REFERENCES `cache` (`cache_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`cdata_codelet`)
        REFERENCES `codelets` (`codelet_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
