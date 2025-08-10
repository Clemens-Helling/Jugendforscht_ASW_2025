import datetime
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from Data.models import Base, Patient, Alarmierung, Teacher, User, Material, SaniProtokoll, Protokoll
from Data.crypto import encrypt, decrypt
engine = create_engine(
    "mysql+pymysql://root:Flecki2022#@localhost:3306/sani_link"
)

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

def add_alert(symptom, alert_type):
    alert = Alarmierung(

        symptom=symptom,
        alert_type=alert_type,
        alert_received=datetime.datetime.now()
    )

    session.add(alert)

    session.flush()
    protokoll = Protokoll(
        alert_id=alert.alert_id
    )
    print(alert.alert_id)

    session.add(protokoll)
    session.commit()
    return alert.alert_id

def generate_unique_pseudonym():
    while True:
        new_uuid = str(uuid.uuid4())
        if not is_uuid_in_patient(new_uuid):
            return new_uuid
# Überprüft, ob ein Patient mit den gleichen Daten existiert
def is_name_in_patient(real_name, real_last_name, birth_day=None):
    enc_name = encrypt(real_name)
    enc_last_name = encrypt(real_last_name)
    print("enc_name:", enc_name)
    print("enc_last_name:", enc_last_name)
    print("birth_day:", birth_day)

    # Alle Patienten abrufen
    patient = session.query(Patient).filter_by(birth_day=birth_day, real_last_name=enc_last_name, real_name=enc_name).first()
    if patient:
        return patient
def is_uuid_in_patient(pseudonym):
    patient = session.query(Patient).filter_by(pseudonym=pseudonym).first()
    if patient:
        return True
def add_patient(real_name, real_last_name, birth_day, alert_id):
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    print("Gefundenes protokoll ")
    patient = is_name_in_patient(real_name, real_last_name, birth_day)
    if patient:
        print("Patient mit diesen Daten existiert bereits.")
        if protokoll:
            protokoll.pseudonym = patient.pseudonym
            session.commit()
        else:
            print("Kein Protokoll mit dieser alert_id gefunden!")
        return
    else:
        enc_name = encrypt(real_name)
        enc_last_name = encrypt(real_last_name)
        patient = Patient(
            pseudonym=generate_unique_pseudonym(),
            real_name=enc_name,
            real_last_name=enc_last_name,
            birth_day=birth_day
        )
        session.add(patient)
        session.flush()
        if protokoll:
            protokoll.pseudonym = patient.pseudonym
            session.commit()
        else:
            print("Kein Protokoll mit dieser alert_id gefunden!")

add_patient(real_name="Vincent", real_last_name="Helling", birth_day=datetime.datetime.strptime("2020-05-01 00:00:00", "%Y-%m-%d %H:%M:%S"), alert_id=add_alert(symptom="Bauchweh", alert_type="erkrankung"))
