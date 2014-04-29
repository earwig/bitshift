"""
Contains information about database schema versions, and SQL queries to update
between them.
"""

VERSION = 2

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
           ADD FOREIGN KEY (`codelet_code_id`)
               REFERENCES `code` (`code_id`)
               ON DELETE RESTRICT ON UPDATE CASCADE""",
        """ALTER TABLE `symbols`
           ADD COLUMN `symbol_end_row` INT UNSIGNED NOT NULL,
           ADD COLUMN `symbol_end_col` INT UNSIGNED NOT NULL"""
    ]
]

if __name__ == "__main__":
    from . import Database

    Database(migrate=True).close()
