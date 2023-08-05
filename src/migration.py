from playhouse.migrate import PostgresqlMigrator, SqliteMigrator, migrate
from peewee import TextField

import logging

class AutoMigration:
    
    def __init__(self, database: object, db_type="postgres") -> None:
        if (db_type == "postgres"):
            self.migrator = PostgresqlMigrator(database)
        else:
            self.migrator = SqliteMigrator(database)
    
    def execute(self):
        try:
            migrate(self.migrator.add_column(
                "reward", "user", TextField(null=True))).execute("on")
        except:
            pass