import os

from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_url = os.environ.get("SYNTHIA_DATABASE_URL", "postgresql://synthia:synthia_dev_password@localhost/evolving_lexicon_db")

Base = declarative_base()

class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True)
    vector = Column(String)
    svnn_t = Column(Float)
    svnn_i = Column(Float)
    svnn_f = Column(Float)

class Context(Base):
    __tablename__ = 'contexts'

    id = Column(Integer, primary_key=True)
    context_id = Column(String, unique=True)
    description = Column(String)

class WordContext(Base):
    __tablename__ = 'word_contexts'

    id = Column(Integer, primary_key=True)
    word = Column(String)
    context_id = Column(String)
    vector = Column(String)
    svnn_t = Column(Float)
    svnn_i = Column(Float)
    svnn_f = Column(Float)

def get_engine():
    return create_engine(db_url)

def create_tables(engine):
    Base.metadata.create_all(engine)

# Example usage to create tables
if __name__ == "__main__":
    engine = get_engine()
    create_tables(engine)
