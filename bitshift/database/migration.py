"""
Contains information about database schema versions, and SQL queries to update
between them.
"""

VERSION = 2

MIGRATIONS = [
    # 1 -> 2
    [
        # drop index on code_hash
        "ALTER TABLE code DROP COLUMN code_hash",
        # change code_id to BIGINT NOT NULL,
        # add key on codelets to codelet_lang
        # add symbol_end_row INT UNSIGNED NOT NULL
        # add symbol_end_col INT UNSIGNED NOT NULL
    ]
]

if __name__ == "__main__":
    from . import Database

    Database(migrate=True).close()
