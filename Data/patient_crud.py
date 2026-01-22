import uuid
import os

from Data.crypto import decrypt, encrypt
from Data.models import Patient, Protokoll
from Data.setup_database import session
from easy_logger.secure_log_client import SecureLogClient
from easy_logger.error_codes import ErrorCodes

# Initialize secure log client
secure_logger = None
if os.path.exists('/home/clemens/dev/Jugendforscht_ASW_2025/keys/client_private_key.pem'):
    try:
        secure_logger = SecureLogClient(
            server_url='http://localhost:5000',
            private_key_path='/home/clemens/dev/Jugendforscht_ASW_2025/keys/client_private_key.pem'
        )
    except Exception as e:
        print(f"Failed to initialize secure logger: {e}")


def clean_name(name):
    return name.replace(" ", "").lower()


def generate_unique_pseudonym():
    while True:
        new_uuid = str(uuid.uuid4())
        if not is_uuid_in_patient(new_uuid):
            return new_uuid


# Überprüft, ob ein Patient mit den gleichen Daten existiert
def is_name_in_patient(real_name, real_last_name, birth_day=None):
    enc_name = encrypt(clean_name(real_name))
    enc_last_name = encrypt(clean_name(real_last_name))

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
        if secure_logger:
            secure_logger.send_log('INFO', 'Patient already exists', {'pseudonym': patient.pseudonym, 'alert_id': alert_id})
        if protokoll:
            protokoll.pseudonym = patient.pseudonym
            session.commit()
        else:
            print("Kein Protokoll mit dieser alert_id gefunden!")
            if secure_logger:
                secure_logger.send_log('ERROR', 'Protokoll not found', {'error_code': ErrorCodes.RESOURCE_NOT_FOUND, 'alert_id': alert_id})
        return
    else:
        enc_name = encrypt(clean_name(real_name))
        enc_last_name = encrypt(clean_name(real_last_name))
        patient = Patient(
            pseudonym=generate_unique_pseudonym(),
            real_name=enc_name,
            real_last_name=enc_last_name,
            birth_day=birth_day,
        )
        session.add(patient)
        session.flush()
        if secure_logger:
            secure_logger.send_log('INFO', 'New patient added', {'pseudonym': patient.pseudonym, 'alert_id': alert_id})
        if protokoll:
            protokoll.pseudonym = patient.pseudonym
            session.commit()
        else:
            print("Kein Protokoll mit dieser alert_id gefunden!")
            if secure_logger:
                secure_logger.send_log('ERROR', 'Protokoll not found', {'error_code': ErrorCodes.RESOURCE_NOT_FOUND, 'alert_id': alert_id})


def get_patient_by_pseudonym(pseudonym):
    """Gibt einen Patienten anhand seines Pseudonyms zurück."""

    patient = session.query(Patient).filter_by(pseudonym=pseudonym).first()
    if patient:
        if secure_logger:
            secure_logger.send_log('INFO', 'Patient retrieved', {'pseudonym': pseudonym})
        return {
            "pseudonym": patient.pseudonym,
            "real_name": decrypt(patient.real_name),
            "real_last_name": decrypt(patient.real_last_name),
            "birth_day": patient.birth_day,
            "created_at": patient.created_at,
        }
    else:
        print("Kein Patient mit diesem Pseudonym gefunden.")
        if secure_logger:
            secure_logger.send_log('WARNING', 'Patient not found', {'error_code': ErrorCodes.RESOURCE_NOT_FOUND, 'pseudonym': pseudonym})
        return None


def get_pseudonym_by_name(real_name, real_last_name, birth_day):
    """Gibt das Pseudonym eines Patienten anhand seines Namens und Geburtsdatums zurück."""
    patient = is_name_in_patient(real_name, real_last_name, birth_day)
    if patient:
        return patient.pseudonym
    else:
        print("Kein Patient mit diesen Daten gefunden.")
        return None


print(get_pseudonym_by_name("Clemens", "Helling", "17.12.2010"))
