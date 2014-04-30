"""
Contains information about database schema versions, and SQL queries to update
between them.
"""

VERSION = 3

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
    ]
]

if __name__ == "__main__":
    from . import Database

    Database(migrate=True).close()
