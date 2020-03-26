from session import db_session
from models import Zip

from pyzipcode import ZipCodeDatabase


zcdb = ZipCodeDatabase()

for z in zcdb.find_zip():
    zip = Zip(zip_code=z.zip)
    db_session.add(zip)

db_session.commit()
