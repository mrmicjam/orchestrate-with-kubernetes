from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool

engine = create_engine('sqlite:///orders.db', poolclass=SingletonThreadPool)

DBSession = sessionmaker(bind=engine)
db_session = DBSession()