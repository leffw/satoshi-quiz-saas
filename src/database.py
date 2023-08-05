from src.configs import DatabaseConfig
from datetime import datetime
from peewee import (
    PostgresqlDatabase, 
    SqliteDatabase, 
    FloatField, 
    Model, 
    TextField, 
    DateTimeField, 
    ForeignKeyField, 
)
from uuid import uuid4

import logging

from src.migration import AutoMigration

class CustomPostgresqlDatabase(PostgresqlDatabase):
    configs = DatabaseConfig

    def execute_sql(self, sql, params=None, commit=None):
        """
        Execute the specified SQL statement with optional parameters and commit the changes.

        Args:
            sql (str): The SQL statement to execute.
            params (tuple, optional): The parameters to substitute in the SQL statement. Defaults to None.
            commit (bool, optional): Whether to commit the changes. Defaults to None.
        """
        try:
            super().execute_sql("SELECT 1;", params, commit)
        except Exception as error:
            logging.error(str(error), exc_info=True)
            if "password" in str(error):
                super().__init__(
                    database=self.configs.DB_NAME,
                    host=self.configs.DB_HOST,
                    port=self.configs.DB_PORT,
                    user=self.configs.DB_USER,
                    password=self.configs.DB_PASS,
                    autorollback=True,
                    thread_safe=True,
                    autoconnect=True
                )
            else:
                self.close()
                self.connect()
            
        return super().execute_sql(sql, params, commit)

class GenericDatabase:
    INSTANCE = None

    def __init__(self, configs: DatabaseConfig):
        """
        Initialize the GenericDatabase class.

        Args:
            configs (DatabaseConfig): The database configurations.
        """
        self.configs = configs
        if "postgres" in self.configs.DB_TYPE:
            self.INSTANCE = CustomPostgresqlDatabase(
                database=self.configs.DB_NAME,
                host=self.configs.DB_HOST,
                port=self.configs.DB_PORT,
                user=self.configs.DB_USER,
                password=self.configs.DB_PASS,
                autorollback=True,
                thread_safe=True,
                autoconnect=True
            )
            self.INSTANCE.configs = self.configs
        else:
            self.INSTANCE = SqliteDatabase(
                database=configs.DB_NAME.split(".")[0] + "." + "sqlite"
            )

database = GenericDatabase(configs=DatabaseConfig()).INSTANCE

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    id = TextField(unique=True, primary_key=True, default=uuid4)
    email = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """
        Save the User model instance with updated timestamps.
        """
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Lndhub(BaseModel):
    id = TextField(unique=True, primary_key=True, default=uuid4)
    user = ForeignKeyField(User)
    url = TextField()
    username = TextField()
    password = TextField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """
        Save the User model instance with updated timestamps.
        """
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Quiz(BaseModel):
    id = TextField(unique=True, primary_key=True, default=uuid4)
    user = ForeignKeyField(User)
    topic = TextField()
    prize = FloatField(default=0)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """
        Save the Quiz model instance with updated timestamps.
        """
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Quizzes(BaseModel):
    id = TextField(unique=True, primary_key=True, default=uuid4)
    quiz = ForeignKeyField(Quiz)
    question = TextField()
    options = TextField()
    answer = TextField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """
        Save the Quizzes model instance with updated timestamps.
        """
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class MemberStack(BaseModel):
    id = TextField(unique=True, primary_key=True, default=uuid4)
    user = ForeignKeyField(User)
    key = TextField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """
        Save the Quizzes model instance with updated timestamps.
        """
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Reward(BaseModel):
    id = TextField(unique=True, primary_key=True, default=uuid4)
    quiz = ForeignKeyField(Quiz)
    value = FloatField(default=0)
    user = TextField(null=True)
    status = TextField(choices=["created", "pending", "settled"])
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """
        Save the Reward model instance 
        with updated timestamps.
        """
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

def create_tables():
    """
    Create tables in the database.
    """
    try:
        AutoMigration(database=database, db_type=DatabaseConfig().DB_TYPE).execute()
    except Exception as error:
        logging.error(str(error))

    database.create_tables([
        User, Lndhub, MemberStack, Quiz, Quizzes, Reward], safe=True)