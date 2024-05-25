from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()
import os


""" postgres_str = "{dialect}://{username}:{password}@{server}/{dbname}".format(
    dialect=os.environ["POSTGRES_DIALECT"],
    server=os.environ["POSTGRES_SERVER"],
    dbname=os.environ["POSTGRES_DBNAME"],
    username=os.environ["POSTGRES_USERNAME"],
    password=os.environ["POSTGRES_PASSWORD"],
) """

engine = create_engine(os.environ["POSTGRES_URL"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
