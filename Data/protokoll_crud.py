import datetime
import json
import os

from IPython.core.magic_arguments import real_name

import Data.users_crud as user_crud
from Data import crypto
from Data.alerts_crud import get_alert_by_id
from Data.crypto import decrypt
from Data.models import (Alarmierung, Material, Patient, Protokoll,
                         ProtokollMaterials, Teacher)
from Data.patient_crud import get_patient_by_pseudonym, get_pseudonym_by_name
from Data.setup_database import session
from Data.users_crud import get_teacher_name_by_id
from easy_logger.easy_logger import EasyLogger
from easy_logger.secure_log_client import SecureLogClient
from easy_logger.error_codes import ErrorCodes
from contextlib import contextmanager

logger = EasyLogger(
    name="UsersCRUD",
    level="INFO",
    log_to_file=True,
    log_dir="logs",
    log_file="database.log"
)

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
@contextmanager
def session_scope():
    """Bietet einen Transaktions-Umfang für die Datenbank-Session."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
def update_status(alert_id, status):
    """Aktualisiert den Status eines Protokolls."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if protokoll:
        protokoll.status = status
        session.commit()
        print(f"Status des Protokolls {alert_id} aktualisiert auf {status}.")
        if secure_logger:
            secure_logger.send_log('INFO', 'Protokoll status updated', {'alert_id': alert_id, 'status': status})
    else:
        print(f"Protokoll mit alert_id {alert_id} nicht gefunden.")
        if secure_logger:
            secure_logger.send_log('WARNING', 'Protokoll not found for status update', {'error_code': ErrorCodes.RESOURCE_NOT_FOUND, 'alert_id': alert_id})


def add_teacher_to_protokoll(alert_id, teacher_id):
    """Fügt einen Lehrer zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        if secure_logger:
            secure_logger.send_log('ERROR', 'Protokoll not found', {'error_code': ErrorCodes.RESOURCE_NOT_FOUND, 'alert_id': alert_id})
        return

    protokoll.teacher_id = teacher_id
    session.commit()
    print(f"Lehrer {teacher_id} zum Protokoll {alert_id} hinzugefügt.")
    if secure_logger:
        secure_logger.send_log('INFO', 'Teacher added to protokoll', {'alert_id': alert_id, 'teacher_id': teacher_id})


def add_measure_to_protokoll(alert_id, measure):
    """Fügt eine Maßnahme zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    protokoll.measures = measure
    session.commit()
    print(f"Maßnahme zum Protokoll {alert_id} hinzugefügt.")
    print(f"Maßnahme gespeichert: {protokoll.measures}")


def add_health_data_to_protokoll(
    alert_id, pulse, spo2, blood_pressure, temperature, bloood_sugar, pain_level
):
    """Fügt Gesundheitsdaten zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        if secure_logger:
            secure_logger.send_log('ERROR', 'Protokoll not found for health data', {'error_code': ErrorCodes.RESOURCE_NOT_FOUND, 'alert_id': alert_id})
        return

    protokoll.pulse = pulse
    protokoll.spo2 = spo2
    protokoll.blood_pressure = blood_pressure
    protokoll.temperature = temperature
    protokoll.blood_sugar = bloood_sugar
    protokoll.pain = pain_level
    session.commit()
    print(f"Gesundheitsdaten zum Protokoll {alert_id} hinzugefügt.")


def add_pickup_measure_to_protokoll(
    alert_id, pickup_measure, parrents_notified_by, parents_notified_at
):
    """Fügt eine Abholmaßnahme zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    protokoll.abhol_massnahme = pickup_measure
    protokoll.parents_notified_by = parrents_notified_by
    protokoll.parents_notified_at = parents_notified_at
    session.commit()
    print(f"Abholmaßnahme zum Protokoll {alert_id} hinzugefügt.")


def add_hospital_to_protokoll(
    alert_id,
    hospital_name,
):
    """Fügt ein Krankenhaus zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    protokoll.hospital = hospital_name

    session.commit()
    print(f"Krankenhaus {hospital_name} zum Protokoll {alert_id} hinzugefügt.")


def add_material_to_protokoll(protokoll_id, material, quantity):
    material_entry = session.query(Material).filter_by(material_name=material).first()
    if not material_entry:
        print(f"Kein Material mit dem Namen {material} gefunden.")
        return

    protokoll_material = ProtokollMaterials(
        protokoll_id=protokoll_id,
        material_id=material_entry.material_id,
        quantity=quantity,
    )

    session.add(protokoll_material)
    session.commit()
    print(
        f"Material {material} (Menge: {quantity}) zum Protokoll {protokoll_id} hinzugefügt."
    )


def close_alert(alert_id):
    """Schließt einen Alarm."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    protokoll.operation_end = datetime.datetime.now()
    protokoll.status = "geschlossen"
    session.commit()
    print(f"Alarm {alert_id} geschlossen.")


def get_protokolls_by_name(first_name, last_name, birth_day):
    """Gibt Protokolle eines Patienten anhand seines Namens und Geburtsdatums zurück."""
    pseudonym = get_pseudonym_by_name(first_name, last_name, birth_day)
    if not pseudonym:
        print("Kein Patient mit diesen Daten gefunden.")
        return []

    protokolls = session.query(Protokoll).filter_by(pseudonym=pseudonym).all()
    return [
        {
            "alert_id": protokoll.alert_id,
            "status": protokoll.status,
            "pseudonym": protokoll.pseudonym,
            "operation_end": protokoll.operation_end,
            "teacher_id": protokoll.teacher_id,
            "pulse": protokoll.pulse,
            "spo2": protokoll.spo2,
            "blood_pressure": protokoll.blood_pressure,
            "temperature": protokoll.temperature,
            "blood_sugar": protokoll.blood_sugar,
            "pain_level": protokoll.pain,
            "abhol_massnahme": protokoll.abhol_massnahme,
            "parents_notified_by": protokoll.parents_notified_by,
            "parents_notified_at": protokoll.parents_notified_at,
            "hospital": protokoll.hospital,
        }
        for protokoll in protokolls
    ]


def get_protokoll_by_alert_id(alert_id):
    """Gibt ein Protokoll anhand der alert_id zurück."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return None

    return {
        "alert_id": protokoll.alert_id,
        "status": protokoll.status,
        "pseudonym": protokoll.pseudonym,
        "operation_end": protokoll.operation_end,
        "teacher_id": protokoll.teacher_id,
        "pulse": protokoll.pulse,
        "spo2": protokoll.spo2,
        "blood_pressure": protokoll.blood_pressure,
        "temperature": protokoll.temperature,
        "blood_sugar": protokoll.blood_sugar,
        "pain_level": protokoll.pain,
        "abhol_massnahme": protokoll.abhol_massnahme,
        "parents_notified_by": protokoll.parents_notified_by,
        "parents_notified_at": protokoll.parents_notified_at,
        "hospital": protokoll.hospital,
        "measures": protokoll.measures,
    }


# python
def safe_decrypt(value):
    if value is None:
        return None
    try:
        return crypto.decrypt(value)
    except Exception:
        try:
            if isinstance(value, (bytes, bytearray)):
                return value.decode("utf-8", errors="replace")
        except Exception:
            pass
        try:
            return str(value)
        except Exception:
            return None


def _to_datetime(value):
    if value is None:
        return None
    if isinstance(value, (datetime.datetime, datetime.date)):
        if isinstance(value, datetime.date) and not isinstance(
            value, datetime.datetime
        ):
            return datetime.datetime(value.year, value.month, value.day)
        return value
    if isinstance(value, (bytes, bytearray)):
        try:
            s = value.decode("utf-8").strip()
        except Exception:
            return None
    else:
        s = str(value).strip()
    fmts = ("%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")
    for fmt in fmts:
        try:
            return datetime.datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def _normalize_person(item):
    if item is None:
        return {"name": "", "funktion": ""}
    if isinstance(item, dict):
        name = (
            item.get("name")
            or item.get("real_name")
            or item.get("first_name")
            or item.get("username")
            or ""
        )
        role = item.get("role") or item.get("funktion") or ""
        return {"name": str(name).strip(), "funktion": str(role).strip()}
    if isinstance(item, (list, tuple)):
        if len(item) >= 2:
            return {"name": str(item[0]).strip(), "funktion": str(item[1]).strip()}
        if len(item) == 1:
            return {"name": str(item[0]).strip(), "funktion": ""}
        return {"name": "", "funktion": ""}
    first = getattr(item, "real_name", None) or getattr(item, "first_name", None) or ""
    last = (
        getattr(item, "real_last_name", None) or getattr(item, "last_name", None) or ""
    )
    role = getattr(item, "role", None) or getattr(item, "funktion", None) or ""
    full = " ".join(filter(None, [str(first).strip(), str(last).strip()])).strip()
    if full:
        return {"name": full, "funktion": str(role) if role is not None else ""}
    return {
        "name": str(item).strip(),
        "funktion": str(role) if role is not None else "",
    }


# -------------------- Die Hauptfunktion --------------------


def prepare_pdf_data(alert_id):
    # Basisdaten
    protokoll = get_protokoll_by_alert_id(alert_id)
    if not protokoll:
        return None

    alert = session.query(Alarmierung).filter_by(alert_id=alert_id).first()
    protokoll_db = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    protokoll_pk = getattr(protokoll_db, "protokoll_id", None)

    patient = (
        session.query(Patient).filter_by(pseudonym=protokoll.get("pseudonym")).first()
    )
    if not patient:
        print(f"Kein Patient mit Pseudonym {protokoll.get('pseudonym')} gefunden.")
        return None

    name = safe_decrypt(getattr(patient, "real_name", None))
    vorname = safe_decrypt(getattr(patient, "real_last_name", None))

    birth_dt = _to_datetime(getattr(patient, "birth_day", None))
    geburtsdatum = birth_dt.strftime("%d.%m.%Y") if birth_dt else None

    teacher_name = "Unbekannt"
    teacher_id = protokoll.get("teacher_id")
    if teacher_id:
        teacher = session.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if teacher:
            teacher_name = f"{teacher.first_name} {teacher.last_name}"

    # Personal laden: Mehrere Fallbacks prüfen
    raw_personal = None
    try:
        if protokoll_pk is not None and hasattr(user_crud, "get_medic_by_protokoll_id"):
            raw_personal = user_crud.get_medic_by_protokoll_id(protokoll_pk)
        if not raw_personal and hasattr(user_crud, "get_medic_by_protokoll_id"):
            raw_personal = user_crud.get_medic_by_protokoll_id(alert_id)
        if not raw_personal and hasattr(user_crud, "get_medic_names_by_alert_id"):
            raw_personal = user_crud.get_medic_names_by_alert_id(alert_id)
        if not raw_personal and hasattr(user_crud, "get_medics_by_alert_id"):
            raw_personal = user_crud.get_medics_by_alert_id(alert_id)
        if not raw_personal and hasattr(user_crud, "get_personal_by_alert"):
            raw_personal = user_crud.get_personal_by_alert(alert_id)
    except Exception as e:
        print("Fehler beim Laden von Personal:", e)
        raw_personal = []

    if raw_personal is None:
        raw_personal = []

    # >>> NEUER TEIL HIER: Konvertierung des Strings in eine Liste <<<
    if isinstance(raw_personal, str):
        try:
            # Versuche, den String als JSON zu parsen
            raw_personal = json.loads(raw_personal)
        except json.JSONDecodeError:
            print("Warnung: Konnte den Personal-String nicht als JSON laden.")
            # Bei einem Fehler eine leere Liste verwenden, um Abstürze zu vermeiden
            raw_personal = []
    # >>> ENDE NEUER TEIL <<<

    # Normalisierung von Personal-Einträgen zu Dicts
    # Die Schleife ruft jetzt die Helferfunktion von außerhalb auf
    personal_list = [_normalize_person(p) for p in raw_personal]

    parents_dt = _to_datetime(protokoll.get("parents_notified_at"))
    operation_dt = _to_datetime(protokoll.get("operation_end"))

    pdf_data = {
        "name": name,
        "vorname": vorname,
        "geburtsdatum": geburtsdatum,
        "klassenlehrer": teacher_name,
        "symptom": alert.symptom if alert else "Unbekannt",
        "alarm_typ": alert.alert_type if alert else "Unbekannt",
        "alarm_eingegangen": alert.alert_received if alert else "Unbekannt",
        "status": protokoll.get("status"),
        "puls": protokoll.get("pulse"),
        "spo2": protokoll.get("spo2"),
        "blutdruck": protokoll.get("blood_pressure"),
        "temperatur": protokoll.get("temperature"),
        "blutzucker": protokoll.get("blood_sugar"),
        "schmerz": protokoll.get("pain_level"),
        "massnahme": protokoll.get("measures"),
        "abholmassnahme": protokoll.get("abhol_massnahme"),
        "eltern_von": protokoll.get("parents_notified_by"),
        "eltern_zeit": parents_dt.strftime("%d.%m.%Y %H:%M") if parents_dt else None,
        "krankenhaus": protokoll.get("hospital"),
        "operation_end": (
            operation_dt.strftime("%d.%m.%Y %H:%M") if operation_dt else None
        ),
        "personal": personal_list,
    }

    print("DEBUG prepare_pdf_data personal count:", len(personal_list))
    logger.info(f"created pdf_data for alert_id {alert_id}")
    return pdf_data


def get_all_open_protokolls():
    """Gibt alle offenen Protokolle zurück."""
    logger.info("=== get_all_open_protokolls wird aufgerufen ===")

    try:
        with session_scope() as db_session:
            protokolls = db_session.query(Protokoll).filter(Protokoll.status != "geschlossen").all()
            logger.info(f"Anzahl gefundener offener Protokolle in DB: {len(protokolls)}")
            result = []

            for protokoll in protokolls:
                try:
                    logger.info(f"Verarbeite Protokoll {protokoll.alert_id} mit Status: {protokoll.status}")
                    patient = get_patient_by_pseudonym(protokoll.pseudonym)
                    alert = get_alert_by_id(protokoll.alert_id)
                    teacher_name = get_teacher_name_by_id(protokoll.teacher_id)

                    # Debug: Patient-Objekt prüfen
                    logger.info(f"Patient-Typ: {type(patient)}")

                    if not patient:
                        patient_name = "Unbekannt"
                        patient_birth_day = "Unbekannt"
                    else:
                        # Prüfen ob patient ein Dict oder Objekt ist
                        if isinstance(patient, dict):
                            # Patient ist ein Dictionary
                            first_name = safe_decrypt(patient.get('real_name')) or "Unbekannt"
                            last_name = safe_decrypt(patient.get('real_last_name')) or "Unbekannt"
                            birth_day = patient.get('birth_day')
                        else:
                            # Patient ist ein Objekt
                            first_name = safe_decrypt(getattr(patient, 'real_name', None)) or "Unbekannt"
                            last_name = safe_decrypt(getattr(patient, 'real_last_name', None)) or "Unbekannt"
                            birth_day = getattr(patient, 'birth_day', None)

                        patient_name = f"{first_name} {last_name}".strip()
                        birth_dt = _to_datetime(birth_day) if birth_day else None
                        patient_birth_day = birth_dt.strftime("%d.%m.%Y") if birth_dt else "Unbekannt"

                    result.append({
                        "alert_id": protokoll.alert_id,
                        "status": protokoll.status,
                        "name": patient_name,
                        "birth_day": patient_birth_day,
                        "symptom": alert.get("symptom") if isinstance(alert, dict) else (alert.symptom if alert else "Unbekannt"),
                        "alert_received": alert.get("alert_received") if isinstance(alert, dict) else (alert.alert_received if alert else "Unbekannt"),
                        "operation_end": protokoll.operation_end,
                        "teacher": teacher_name or "Unbekannt",
                        "pulse": protokoll.pulse,
                        "spo2": protokoll.spo2,
                        "blood_pressure": protokoll.blood_pressure,
                        "temperature": protokoll.temperature,
                        "blood_sugar": protokoll.blood_sugar,
                        "pain_level": protokoll.pain,
                        "abhol_massnahme": protokoll.abhol_massnahme,
                        "parents_notified_by": protokoll.parents_notified_by,
                        "parents_notified_at": protokoll.parents_notified_at,
                        "hospital": protokoll.hospital,
                    })
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten von Protokoll {protokoll.alert_id}: {e}")
                    continue

            logger.info(f"=== get_all_open_protokolls beendet - {len(result)} Protokolle zurückgegeben ===")
            return result

    except Exception as e:
        logger.error(f"Fehler beim Laden der offenen Protokolle: {e}")
        return []
def convert_alert_to_protokoll_id(alert_id):
    """Konvertiert eine Alert-ID in eine Protokoll-ID."""
    with session_scope() as s:
        protokoll = s.query(Protokoll).filter_by(alert_id=alert_id).first()
        if protokoll:
            return protokoll.protokoll_id
        else:
            print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
            return None

if __name__ == "__main__":
    print(convert_alert_to_protokoll_id(145))
