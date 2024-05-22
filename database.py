from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRES_DIALECT = "postgresql"
POSTGRES_SERVER = "ep-lucky-dew-a18g6gm7.ap-southeast-1.aws.neon.tech"
POSTGRES_DBNAME = "neue"
POSTGRES_USERNAME = "neue_owner"
POSTGRES_PASSWORD = "p6kZBXP5eOEY"
""" POSTGRES_DIALECT = "postgresql"
POSTGRES_SERVER = "localhost"
POSTGRES_DBNAME = "anilist2"
POSTGRES_USERNAME = "postgres"
POSTGRES_PASSWORD = "eyeDGAF<3" """


postgres_str = "{dialect}://{username}:{password}@{server}/{dbname}".format(
    dialect=POSTGRES_DIALECT,
    server=POSTGRES_SERVER,
    dbname=POSTGRES_DBNAME,
    username=POSTGRES_USERNAME,
    password=POSTGRES_PASSWORD,
)

engine = create_engine(postgres_str)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
