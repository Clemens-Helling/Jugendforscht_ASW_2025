import datetime
import uuid

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from Data.crypto import decrypt, encrypt
from Data.models import (Alarmierung, Base, Material, Patient, Protokoll,
                         SaniProtokoll, Teacher, User)
from easy_logger.secure_log_client import SecureLogClient

logger = SecureLogClient(
    server_url = "http://192.168.178.112:5000",
    private_key_path = "keys/client_private_key.pem"
)

engine = create_engine("mysql+pymysql://root:clemens1712@localhost:3306/sani_link")
try:
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    logger.send_log("INFO","Datenbank verbindung hergestellt")
except Exception as e:
    logger.send_log("INFO","Datenbank verbindung hergestellt")




