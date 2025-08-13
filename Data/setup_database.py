import datetime
import uuid

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from Data.crypto import decrypt, encrypt
from Data.models import (
    Alarmierung,
    Base,
    Material,
    Patient,
    Protokoll,
    SaniProtokoll,
    Teacher,
    User,
)

engine = create_engine("mysql+pymysql://root:Flecki2022#@localhost:3306/sani_link")

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
