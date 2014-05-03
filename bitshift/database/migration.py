"""
Contains information about database schema versions, and SQL queries to update
between them.
"""

VERSION = 5

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
    ]
]

if __name__ == "__main__":
    from . import Database

    Database(migrate=True).close()
