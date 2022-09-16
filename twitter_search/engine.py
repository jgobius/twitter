from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import os

class DatabaseEngine:

    @property
    def engine(self) -> Engine:

        """
        Method to create a database connection.

        Returns:
            Engine: the database engine.
        """        

        engine = create_engine(f'mssql+pyodbc://{os.environ.get("USER")}:{os.environ.get("PASSWORD")}@{os.environ.get("SERVER_NAME")}/{os.environ.get("DATABASE_NAME")}?driver={os.environ.get("DRIVER_NAME")}')

        return engine