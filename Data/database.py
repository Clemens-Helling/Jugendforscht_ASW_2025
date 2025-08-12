import datetime
import uuid

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from Data.crypto import decrypt, encrypt
from Data.models import (Alarmierung, Base, Material, Patient, Protokoll,
                         SaniProtokoll, Teacher, User)

engine = create_engine("mysql+pymysql://root:Flecki2022#@localhost:3306/sani_link")

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


def add_alert(symptom, alert_type):
    alert = Alarmierung(
        symptom=symptom, alert_type=alert_type, alert_received=datetime.datetime.now()
    )

    session.add(alert)

    session.flush()
    protokoll = Protokoll(alert_id=alert.alert_id)
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
    patient = (
        session.query(Patient)
        .filter_by(
            birth_day=birth_day, real_last_name=enc_last_name, real_name=enc_name
        )
        .first()
    )
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
            birth_day=birth_day,
        )
        session.add(patient)
        session.flush()
        if protokoll:
            protokoll.pseudonym = patient.pseudonym
            session.commit()
        else:
            print("Kein Protokoll mit dieser alert_id gefunden!")


def get_patient_by_pseudonym(pseudonym):
    """Gibt einen Patienten anhand seines Pseudonyms zurück."""

    patient = session.query(Patient).filter_by(pseudonym=pseudonym).first()
    if patient:
        return {
            "pseudonym": patient.pseudonym,
            "real_name": decrypt(patient.real_name),
            "real_last_name": decrypt(patient.real_last_name),
            "birth_day": patient.birth_day,
            "created_at": patient.created_at,
        }
    else:
        print("Kein Patient mit diesem Pseudonym gefunden.")
        return None

def get_alerts():
    """Gibt alle Alarmierungen zurück."""
    alerts = session.query(Alarmierung).all()
    return [
        {
            "alert_id": alert.alert_id,
            "alert_received": alert.alert_received,
            "alert_type": alert.alert_type,
            "symptom": alert.symptom,
        }
        for alert in alerts
    ]
def add_teacher(first_name, last_name, house):
    """Fügt einen Lehrer hinzu."""
    teacher = Teacher(first_name=first_name, last_name=last_name, house=house)
    session.add(teacher)
    session.commit()
    print(f"Lehrer {first_name} {last_name} hinzugefügt.")

def add_user(name, last_name, lernbegleiter, kartennummer, permission):
    """Fügt einen Benutzer hinzu."""
    user = User(
        name=name,
        last_name=last_name,
        lernbegleiter=lernbegleiter,
        karten_nummer=kartennummer,
        permission=permission,
    )
    session.add(user)
    session.commit()
    print(f"Benutzer {name} {last_name} hinzugefügt.")



def add_sani1(card_number, alert_id):
    sani = session.query(User).filter_by(karten_nummer=card_number).first()

    if not sani:
        print(f"Kein Benutzer mit Karten­nummer {card_number} gefunden.")
        return

    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    sani_protokoll = SaniProtokoll(
        sani1=sani.User_ID,
        protokoll_id=protokoll.protokoll_id
    )
    protokoll.medic_id = sani_protokoll.sani_protokoll_id

    session.add(sani_protokoll)
    session.commit()
    print(f"Sani 1 ({sani.name} {sani.last_name}) zum Protokoll {protokoll.protokoll_id} hinzugefügt.")
if __name__ == "__main__":
    add_sani1("1234567890", 27)

# add_user(name="Max",last_name="Mustermann",lernbegleiter="1",kartennummer="1234567890",permission="admin",)
# add_patient(real_name="Vincent", real_last_name="Helling", birth_day=datetime.datetime.strptime("2020-05-01 00:00:00", "%Y-%m-%d %H:%M:%S"), alert_id=add_alert(symptom="Bauchweh", alert_type="erkrankung"))
