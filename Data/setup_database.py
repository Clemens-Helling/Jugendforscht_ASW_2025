import datetime
import uuid

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from Data.crypto import decrypt, encrypt
from Data.models import (Alarmierung, Base, Material, Patient, Protokoll,
                         SaniProtokoll, Teacher, User)
from easy_logger.easy_logger import EasyLogger

logger = EasyLogger(
    name="DatabaseSetup",
    level="INFO",
    log_to_file=True,
    log_to_console=False,
    log_dir="logs",
    log_file="database.log"
)

engine = create_engine("mysql+pymysql://root:clemens1712@localhost:3306/sani_link")
try:
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    logger.info("Session created!")
except Exception as e:
    logger.critical("Datenbankverbindung fehlgeschlagen")




