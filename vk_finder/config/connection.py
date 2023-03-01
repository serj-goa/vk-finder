import os
import sqlalchemy

from dotenv import find_dotenv, load_dotenv
from sqlalchemy.orm import sessionmaker


load_dotenv(find_dotenv())

engine = sqlalchemy.create_engine(os.getenv('DSN'))
Session = sessionmaker(bind=engine)
