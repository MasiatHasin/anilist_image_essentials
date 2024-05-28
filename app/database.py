from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()
import os

postgres_str = "postgresql://postgres:eyeDGAF<3@localhost/anilist"

engine = create_engine(os.environ["MYSQL_URL"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
