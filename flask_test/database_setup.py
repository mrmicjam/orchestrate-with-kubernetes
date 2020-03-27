from models import *
from session import *
from flask import Flask, session
from flask_session import SqlAlchemySessionInterface


Base.metadata.create_all(engine)
