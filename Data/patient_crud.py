from Data.crypto import decrypt, encrypt
from Data.models import Patient, Protokoll
from Data.setup_database import session
import uuid


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


add_patient("Kerstin", "Helling", "1978-10-15", 27)
