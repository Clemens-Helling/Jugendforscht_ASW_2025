from Data.setup_database import session
from Data.models import Protokoll, Patient, Material, ProtokollMaterials, Alarmierung, Teacher
from Data.patient_crud import get_pseudonym_by_name,get_patient_by_pseudonym
import Data.users_crud as user_crud
from Data import crypto
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
    protokoll.pain = pain_level
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



def add_material_to_protokoll(protokoll_id, material, quantity):
    material_entry = session.query(Material).filter_by(material_name=material).first()
    if not material_entry:
        print(f"Kein Material mit dem Namen {material} gefunden.")
        return

    protokoll_material = ProtokollMaterials(
        protokoll_id=protokoll_id,
        material_id=material_entry.material_id,
        quantity=quantity
    )

    session.add(protokoll_material)
    session.commit()
    print(f"Material {material} (Menge: {quantity}) zum Protokoll {protokoll_id} hinzugefügt.")

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
        "hospital": protokoll.hospital
    }

# python
# python
# python
# python
# python
def prepare_pdf_data(alert_id):
    import datetime
    protokoll = get_protokoll_by_alert_id(alert_id)
    if not protokoll:
        return None

    alert = session.query(Alarmierung).filter_by(alert_id=alert_id).first()

    patient = session.query(Patient).filter_by(pseudonym=protokoll.get("pseudonym")).first()
    if not patient:
        print(f"Kein Patient mit Pseudonym {protokoll.get('pseudonym')} gefunden.")
        return None

    def _to_datetime(value):
        if value is None:
            return None
        if isinstance(value, (datetime.datetime, datetime.date)):
            if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
                return datetime.datetime(value.year, value.month, value.day)
            return value
        if isinstance(value, bytes):
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

    birth_dt = _to_datetime(getattr(patient, "birth_day", None))
    geburtsdatum = birth_dt.strftime("%d.%m.%Y") if birth_dt else None

    teacher_name = "Unbekannt"
    teacher_id = protokoll.get("teacher_id")
    if teacher_id:
        teacher = session.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if teacher:
            teacher_name = f"{teacher.first_name} {teacher.last_name}"

    # Rohdaten der beteiligten Personen holen
    raw_personal = []
    try:
        raw_personal = user_crud.get_medic_by_protokoll_id(alert_id) or []
    except Exception:
        raw_personal = []

    # Normalisieren zu Dicts mit Schlüssel "name" und "role"
    def _normalize_person(item):
        if item is None:
            return {"name": "", "role": ""}
        if isinstance(item, dict):
            name = item.get("name") or item.get("real_name") or item.get("first_name") or item.get("username") or ""
            role = item.get("role") or item.get("funktion") or ""
            return {"name": str(name).strip(), "role": str(role).strip()}
        # ORM-/Objekt-Fall: versuche Vorname/Nachname bzw. Rollenattribute
        if hasattr(item, "__dict__") or any(hasattr(item, attr) for attr in ("first_name", "real_name", "last_name", "real_last_name", "username")):
            first = getattr(item, "real_name", None) or getattr(item, "first_name", None) or ""
            last = getattr(item, "real_last_name", None) or getattr(item, "last_name", None) or ""
            full = " ".join(filter(None, [str(first).strip(), str(last).strip()])).strip()
            role = getattr(item, "role", "") or getattr(item, "funktion", "")
            return {"name": full or str(item), "role": str(role)}
        # Liste/Tuple: joinen
        if isinstance(item, (list, tuple)):
            parts = [str(x).strip() for x in item if x is not None]
            return {"name": " ".join(parts), "role": ""}
        # primitive Typen (z.B. String)
        return {"name": str(item).strip(), "role": ""}

    personal_list = [_normalize_person(p) for p in raw_personal]

    parents_dt = _to_datetime(protokoll.get("parents_notified_at"))
    operation_dt = _to_datetime(protokoll.get("operation_end"))

    pdf_data = {
        "name": crypto.decrypt(getattr(patient, "real_name", None)),
        "vorname": crypto.decrypt(getattr(patient, "real_last_name", None)),
        "geburtsdatum": geburtsdatum,
        "klassenlehrer": teacher_name,
        "symptom": alert.symptom if alert else "Unbekannt",
        "alarm_type": alert.alert_type if alert else "Unbekannt",
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
        "operation_end": operation_dt.strftime("%d.%m.%Y %H:%M") if operation_dt else None,
        "personal": personal_list
    }

    return pdf_data
