import datetime
import uuid
import os

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from Data.crypto import decrypt, encrypt
from Data.models import (Alarmierung, Base, Material, Patient, Protokoll,
                         SaniProtokoll, Teacher, User)
from easy_logger.secure_log_client import SecureLogClient

logger = SecureLogClient(
    server_url = "http://192.168.178.112:5000",
    private_key_path = "keys/client_private_key.pem"
)

# Lade Umgebungsvariablen
load_dotenv('sanilink.env')

engine = None
Session = None
session = None
db_connection_error = None

def get_db_connection_string():
    """Erstellt die Datenbankverbindungs-URL aus Umgebungsvariablen"""
    user = os.getenv('DB_USER', 'sani')
    password = os.getenv('DB_PASSWORD', 'clemens1712')
    host = os.getenv('DB_HOST', '192.168.178.112')
    port = os.getenv('DB_PORT', '3606')
    database = os.getenv('DB_NAME', 'sani_link')
    
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

try:
    connection_string = get_db_connection_string()
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    logger.send_log("INFO","Datenbank verbindung hergestellt")
except Exception as e:
    db_connection_error = str(e)
    logger.send_log("ERROR", f"Datenbank verbindung fehlgeschlagen: {e}")




