import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data.models import Base, Alarmierungen, Pseudonymization
import datetime
engine = create_engine('mysql+pymysql://root:Flecki2022#@localhost:3306/notifyer')

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
 
def add_alarm(name, lastname,  symptom):
    unique_id = str(uuid.uuid4())

    if not is_uuid_in_pseudonymization(unique_id) and not is_name_in_pseudonymization(name):
        entry = Pseudonymization(real_name=name,real_last_name= lastname, pseudonym=unique_id)
        session.add(entry)
        session.commit()
    
    pseudonym = session.query(Pseudonymization).filter_by(real_name=name).first().pseudonym
     
    alarm = Alarmierungen(name=pseudonym, lastname=pseudonym,  symptom=symptom, )
    session.add(alarm)
    session.commit()
def is_name_in_pseudonymization(name):
    # Überprüfen, ob der Name in der Pseudonymization-Tabelle vorhanden ist
    result = session.query(Pseudonymization).filter_by(real_name=name).first()
    print(result)
    if result is not None:
        return True
    

def is_uuid_in_pseudonymization(unique_id):
    # Überprüfen, ob die UUID in der Pseudonymization-Tabelle vorhanden ist
    result = session.query(Pseudonymization).filter_by(pseudonym=unique_id).first()
    if result is not None:
        return True