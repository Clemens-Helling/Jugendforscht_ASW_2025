import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data.models import Base, Alarmierungen, Pseudonymization
import datetime
from Data import crypto

print("Database.py")
engine = create_engine('mysql+pymysql://root:Flecki2022#@localhost:3306/notifyer')
 
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

def add_alarm(name, lastname, symptom):
    unique_id = str(uuid.uuid4())
    global pseudonym
    if not is_uuid_in_pseudonymization(unique_id) and not is_name_in_pseudonymization(name):
        encrypted_name = crypto.encrypt(name)
        encrypted_last_name = crypto.encrypt(lastname)
        entry = Pseudonymization(real_name=encrypted_name, real_last_name=encrypted_last_name, pseudonym=unique_id)
        alarm = Alarmierungen(name=unique_id, lastname=unique_id, symptom=symptom)
        session.add(alarm)
        session.add(entry)
        session.commit()
    else:
        encrypted_name = crypto.encrypt(name)
        print(encrypted_name)
        
        pseudonym = session.query(Pseudonymization).filter_by(real_name=encrypted_name).first().pseudonym
        
        print(pseudonym)
        alarm = Alarmierungen(name=pseudonym, lastname=pseudonym, symptom=symptom)
        session.add(alarm)
        session.commit()

def is_name_in_pseudonymization(name):
    encrypted_name = crypto.encrypt(name)
    result = session.query(Pseudonymization).filter_by(real_name=encrypted_name).first()
    print(result)
    return result is not None

def is_uuid_in_pseudonymization(unique_id):
    result = session.query(Pseudonymization).filter_by(pseudonym=unique_id).first()
    return result is not None