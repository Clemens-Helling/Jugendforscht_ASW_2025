from Data.setup_database import session
from Data.models import Protokoll, Patient
from Data.patient_crud import get_pseudonym_by_name
import datetime

def update_status(alert_id, status):
    """Aktualisiert den Status eines Protokolls."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if protokoll:
        protokoll.status = status
        session.commit()
        print(f"Status des Protokolls {alert_id} aktualisiert auf {status}.")
    else:
        print(f"Protokoll mit alert_id {alert_id} nicht gefunden.")

def add_teacher_to_protokoll(alert_id, teacher_id):
    """Fügt einen Lehrer zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    protokoll.teacher_id = teacher_id
    session.commit()
    print(f"Lehrer {teacher_id} zum Protokoll {alert_id} hinzugefügt.")


def add_health_data_to_protokoll(alert_id, pulse, spo2, blood_pressure, temperature, bloood_sugar, pain_level ):
    """Fügt Gesundheitsdaten zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    protokoll.pulse = pulse
    protokoll.spo2 = spo2
    protokoll.blood_pressure = blood_pressure
    protokoll.temperature = temperature
    protokoll.blood_sugar = bloood_sugar
    protokoll.pain_level = pain_level
    session.commit()
    print(f"Gesundheitsdaten zum Protokoll {alert_id} hinzugefügt.")

def add_pickup_measure_to_protokoll(alert_id, pickup_measure, parrents_notified_by, parents_notified_at):
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

def add_hospital_to_protokoll(alert_id, hospital_name,):
    """Fügt ein Krankenhaus zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    protokoll.hospital= hospital_name

    session.commit()
    print(f"Krankenhaus {hospital_name} zum Protokoll {alert_id} hinzugefügt.")

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
            "hospital": protokoll.hospital
        }
        for protokoll in protokolls
    ]
print(get_protokolls_by_name("Clemens", "Helling", "17.12.2010"))