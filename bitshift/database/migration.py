"""
Contains information about database schema versions, and SQL queries to update
between them.
"""

VERSION = 8

MIGRATIONS = [
    # 1 -> 2
    [
        """ALTER TABLE `codelets`
           DROP FOREIGN KEY `codelets_ibfk_1`""",
        """ALTER TABLE `code`
           DROP KEY `code_hash`,
           DROP COLUMN `code_hash`,
           MODIFY COLUMN `code_id` BIGINT NOT NULL""",
        """ALTER TABLE `codelets`
           MODIFY COLUMN `codelet_code_id` BIGINT NOT NULL,
           ADD KEY (`codelet_lang`),
           ADD CONSTRAINT `codelets_ibfk_1` FOREIGN KEY (`codelet_code_id`)
               REFERENCES `code` (`code_id`)
               ON DELETE RESTRICT ON UPDATE CASCADE""",
        """ALTER TABLE `symbols`
           ADD COLUMN `symbol_end_row` INT UNSIGNED NOT NULL,
           ADD COLUMN `symbol_end_col` INT UNSIGNED NOT NULL"""
    ],
    # 2 -> 3
    [
        """ALTER TABLE `symbols`
           DROP FOREIGN KEY `symbols_ibfk_1`,
           CHANGE COLUMN `symbol_codelet` `symbol_code` BIGINT NOT NULL,
           ADD CONSTRAINT `symbols_ibfk_1` FOREIGN KEY (`symbol_code`)
               REFERENCES `code` (`code_id`)
               ON DELETE CASCADE ON UPDATE CASCADE"""
    ],
    # 3 -> 4
    [
        """ALTER TABLE `symbols`
           DROP COLUMN `symbol_row`,
           DROP COLUMN `symbol_col`,
           DROP COLUMN `symbol_end_row`,
           DROP COLUMN `symbol_end_col`""",
        """CREATE TABLE `symbol_locations` (
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
           ) ENGINE=InnoDB"""
    ],
    # 4 -> 5
    [
        """ALTER TABLE `origins`
           MODIFY COLUMN `origin_name` VARCHAR(64) DEFAULT NULL,
           MODIFY COLUMN `origin_url` VARCHAR(512) DEFAULT NULL,
           MODIFY COLUMN `origin_url_base` VARCHAR(512) DEFAULT NULL"""
    ],
    # 5 -> 6
    [
        """ALTER TABLE `code`
           ADD COLUMN `code_lang` SMALLINT UNSIGNED DEFAULT NULL
               AFTER `code_id`,
           ADD KEY (`code_lang`)""",
        """ALTER TABLE `codelets`
           DROP KEY `codelet_lang`,
           DROP COLUMN `codelet_lang`""",
        """ALTER TABLE `cache_data`
           DROP FOREIGN KEY `cache_data_ibfk_1`""",
        """ALTER TABLE `cache`
           MODIFY COLUMN `cache_id` BIGINT NOT NULL,
           DROP COLUMN `cache_hash`,
           DROP COLUMN `cache_last_used`,
           MODIFY COLUMN `cache_count_mnt` SMALLINT UNSIGNED NOT NULL""",
        """ALTER TABLE `cache_data`
           MODIFY COLUMN `cdata_cache` BIGINT NOT NULL,
           ADD PRIMARY KEY (`cdata_cache`, `cdata_codelet`),
           ADD CONSTRAINT `cache_data_ibfk_1` FOREIGN KEY (`cdata_codelet`)
               REFERENCES `codelets` (`codelet_id`)
               ON DELETE CASCADE ON UPDATE CASCADE""",
        """CREATE EVENT `flush_cache`
           ON SCHEDULE EVERY 1 HOUR
           DO
               DELETE FROM `cache`
                   WHERE `cache_created` < DATE_SUB(NOW(), INTERVAL 1 DAY);"""
    ],
    # 6 -> 7
    [
        """DELETE FROM `cache`""",
        """ALTER TABLE `cache_data`
           ADD COLUMN `cdata_index` TINYINT UNSIGNED NOT NULL
               AFTER `cdata_codelet`"""
    ],
    # 7 -> 8
    [
        """ALTER TABLE `origins`
           DROP COLUMN `origin_image`"""
    ]
]

if __name__ == "__main__":
    from . import Database

    Database(migrate=True).close()
