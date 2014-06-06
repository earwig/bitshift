-- Schema version 9

CREATE DATABASE `bitshift` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `bitshift`;

CREATE TABLE `version` (
    `version` INT UNSIGNED NOT NULL
) ENGINE=InnoDB;
INSERT INTO `version` VALUES (9);

CREATE TABLE `origins` (
    `origin_id` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `origin_name` VARCHAR(64) DEFAULT NULL,
    `origin_url` VARCHAR(512) DEFAULT NULL,
    `origin_url_base` VARCHAR(512) DEFAULT NULL,
    PRIMARY KEY (`origin_id`)
) ENGINE=InnoDB;
INSERT INTO `origins` VALUES (1, NULL, NULL, NULL);

CREATE TABLE `code` (
    `code_id` BIGINT NOT NULL,
    `code_lang` SMALLINT UNSIGNED DEFAULT NULL,
    `code_code` MEDIUMTEXT NOT NULL,
    PRIMARY KEY (`code_id`),
    KEY (`code_lang`),
    FULLTEXT KEY (`code_code`)
) ENGINE=InnoDB;

CREATE TABLE `codelets` (
    `codelet_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `codelet_name` VARCHAR(300) NOT NULL,
    `codelet_code_id` BIGINT NOT NULL,
    `codelet_origin` TINYINT UNSIGNED NOT NULL,
    `codelet_url` VARCHAR(512) NOT NULL,
    `codelet_rank` FLOAT NOT NULL,
    `codelet_date_created` DATETIME DEFAULT NULL,
    `codelet_date_modified` DATETIME DEFAULT NULL,
    PRIMARY KEY (`codelet_id`),
    FULLTEXT KEY (`codelet_name`),
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
    `symbol_code` BIGINT NOT NULL,
    `symbol_type` TINYINT UNSIGNED NOT NULL,
    `symbol_name` VARCHAR(512) NOT NULL,
    PRIMARY KEY (`symbol_id`),
    KEY (`symbol_type`, `symbol_name`(32)),
    FOREIGN KEY (`symbol_code`)
        REFERENCES `code` (`code_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `symbol_locations` (
    `sloc_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `sloc_symbol` BIGINT UNSIGNED NOT NULL,
    `sloc_type` TINYINT UNSIGNED NOT NULL,
    `sloc_row` INT UNSIGNED NOT NULL,
    `sloc_col` INT UNSIGNED NOT NULL,
    `sloc_end_row` INT UNSIGNED NOT NULL,
    `sloc_end_col` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`sloc_id`),
    FOREIGN KEY (`sloc_symbol`)
        REFERENCES `symbols` (`symbol_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `cache` (
    `cache_id` BIGINT NOT NULL,
    `cache_count_mnt` SMALLINT UNSIGNED NOT NULL,
    `cache_count_exp` TINYINT UNSIGNED NOT NULL,
    `cache_created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`cache_id`)
) ENGINE=InnoDB;

CREATE TABLE `cache_data` (
    `cdata_cache` BIGINT NOT NULL,
    `cdata_codelet` BIGINT UNSIGNED NOT NULL,
    `cdata_index` TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY (`cdata_cache`, `cdata_codelet`),
    FOREIGN KEY (`cdata_cache`)
        REFERENCES `cache` (`cache_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`cdata_codelet`)
        REFERENCES `codelets` (`codelet_id`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

DELIMITER //
CREATE PROCEDURE `empty_database`()
    BEGIN
        DELETE FROM `codelets`;
        DELETE FROM `code`;
        DELETE FROM `cache`;
        ALTER TABLE `codelets` AUTO_INCREMENT = 1;
        ALTER TABLE `authors` AUTO_INCREMENT = 1;
        ALTER TABLE `symbols` AUTO_INCREMENT = 1;
        ALTER TABLE `symbol_locations` AUTO_INCREMENT = 1;
    END//
DELIMITER ;

CREATE EVENT `flush_cache`
    ON SCHEDULE EVERY 1 HOUR
    DO
        DELETE FROM `cache`
            WHERE `cache_created` < DATE_SUB(NOW(), INTERVAL 1 DAY);
