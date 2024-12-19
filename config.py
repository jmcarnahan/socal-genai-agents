

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import text
from dotenv import load_dotenv
from openai import OpenAI
import os
import logging

load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.engines = {}
            metadata_db_path = os.getenv('METADATA_FILE', '.metadata.db')
            cls._instance.engines['default'] = create_engine(f"sqlite:///{metadata_db_path}", echo=True)
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("API key is not set. Please ensure the OPENAI_API_KEY is set in the .env file.")
            cls._instance.openai_client = OpenAI(api_key=api_key, project=os.getenv('OPENAI_PROJECT'))
        return cls._instance

    @classmethod
    def initialize(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)

    @classmethod
    def get_db_engine(cls, db_path="default"):
        cls.initialize()  # Ensure _instance is initialized
        if db_path not in cls._instance.engines:
            engine = create_engine(f'sqlite:///{db_path}', echo=True)
            cls._instance.engines[db_path] = engine
        return cls._instance.engines[db_path]

    @classmethod
    def get_db_session(cls, db_path="default"):
        cls.initialize()  # Ensure _instance is initialized
        engine = cls.get_db_engine(db_path)
        Session = scoped_session(sessionmaker(bind=engine))
        return Session()

    @classmethod
    def close_db_engine(cls, db_path="default"):
        cls.initialize()  # Ensure _instance is initialized
        if db_path in cls._instance.engines:
            cls._instance.engines[db_path].dispose()
            del cls._instance.engines[db_path]

    @classmethod
    def get_openai_client(cls):
        cls.initialize()
        return cls._instance.openai_client
    
    @classmethod
    def get_openai_deployment(cls):
        return os.getenv('OPENAI_DEPLOYMENT', 'gpt-4o')
    
    @classmethod
    def get_openai_project(cls):
        return os.getenv('OPENAI_PROJECT')


if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine.Engine').propagate = False
    session = Config.get_db_session("test.db")
    session.execute(text("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)"))
    session.execute(text("INSERT INTO test (name) VALUES ('test')"))
    session.commit()
    # do a query to make sure the data was inserted
    result = session.execute(text("SELECT * FROM test")).fetchall()
    print(result)
    session.close()
    Config.close_db_engine("test.db")
    Config.get_openai_client()

