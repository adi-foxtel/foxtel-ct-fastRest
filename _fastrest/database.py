import os

import databases
import sqlalchemy

DATABASE_URL = os.getenv("DATABASE_URL")


# Define the URL for our SQLite database. This is a file path which makes
# the database in a file called data.db in the current directory.
DATABASE_URL = "sqlite:///data.db"

# MetaData is a container object that keeps together different features of a database being described.
metadata = sqlalchemy.MetaData()

task_table = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer),
    sqlalchemy.Column("start_time", sqlalchemy.DateTime),
    sqlalchemy.Column("end_time", sqlalchemy.DateTime)
)

# You don't need check_same_thread=False when using PostgreSQL.
#engine = sqlalchemy.create_engine(DATABASE_URL)

# Create an engine that stores data in the local directory's data.db file. 
# "check_same_thread" is set to False as SQLite connections are not thread-safe by default. 
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create all tables stored in this metadata in the actual file.
metadata.create_all(engine)

# Initialize a database connection.
database = databases.Database(DATABASE_URL)

