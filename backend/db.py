import os
import urllib.parse

from sqlalchemy import create_engine
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(__file__)

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

encoded_password = urllib.parse.quote_plus(
    DB_PASSWORD
)

connection_string = (
    f"mysql+pymysql://{DB_USER}:"
    f"{encoded_password}@{DB_HOST}/{DB_NAME}"
)

engine = create_engine(
    connection_string,
    pool_pre_ping=True,
    pool_recycle=3600
)