import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data.models import Base, Alarmierungen, Pseudonymization, Medics
import datetime
from Data import crypto


engine = create_engine('mysql+pymysql://sani_base:qEkfan-korcy9-kaswyt@localhost:3306/Notifyer')

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

def add_alarm(name, lastname, symptom):
    """Fügt einen Alarm zur Datenbank hinzu.

    Parameters
    ----------
    name : str  
        Der Name des Patienten.
    lastname : str  
        der Nachname des Patienten.
    symptom : str
        Das Symptom des Patienten.
    """
    unique_id = str(uuid.uuid4())
    global pseudonym
    if not is_uuid_in_pseudonymization(unique_id) and not is_name_in_pseudonymization(name):
        encrypted_name = crypto.encrypt(name)
        encrypted_last_name = crypto.encrypt(lastname)
        entry = Pseudonymization(real_name=encrypted_name, real_last_name=encrypted_last_name, pseudonym=unique_id)
        alarm = Alarmierungen(name=unique_id, lastname=unique_id, symptom=symptom, status= "aktive")
        session.add(alarm)
        session.add(entry)
        session.commit()
    else:
        encrypted_name = crypto.encrypt(name)
        print(encrypted_name)
        
        pseudonym = session.query(Pseudonymization).filter_by(real_name=encrypted_name).first().pseudonym
        
        print(pseudonym)
        alarm = Alarmierungen(name=pseudonym, lastname=pseudonym, symptom=symptom, status= "aktive")
        session.add(alarm)
        session.commit()

def is_name_in_pseudonymization(name):
    """Überprüft, ob ein Name bereits in der Pseudonymisierungstabelle vorhanden ist.

    Parameters
    ----------
    name : str
        Name, der überprüft werden soll.

    Returns
    -------
    str
        Ergebnis der Überprüfung.
    """
    encrypted_name = crypto.encrypt(name)
    result = session.query(Pseudonymization).filter_by(real_name=encrypted_name).first()
    print(result)
    return result is not None

def is_uuid_in_pseudonymization(unique_id):
    """Überprüft, ob ein Pseudonym bereits in der Pseudonymisierungstabelle vorhanden ist.

    Parameters
    ----------
    unique_id : str
        Das Pseudonym, das überprüft werden soll.

    Returns
    -------
    _type_
        das Ergebnis der Überprüfung.
    """
    result = session.query(Pseudonymization).filter_by(pseudonym=unique_id).first()
    return result is not None

def search_alerts(firstname, lastname):
    """Sucht nach Alarmen in der Datenbank.

    Parameters
    ----------
    firstname : str
        Vorname des Patienten dessen Daten gesucht werden sollen.
    lastname : str
        Nachname des Patienten dessen Daten gesucht werden sollen.

    Returns
    -------
    dict
        Ein Dictionary mit den gefunden
    """
    encrypted_name = crypto.encrypt(firstname)
    encrypted_lastname = crypto.encrypt(lastname)
    
    result = session.query(Pseudonymization).filter_by(real_name=encrypted_name, real_last_name=encrypted_lastname).first()
    
    if result is not None:
        pseudonym = result.pseudonym
        alerts = session.query(Alarmierungen).filter_by(name=pseudonym).all()
        
        # Entschlüsseln der Namen und Nachnamen
        encrypted_name = result.real_name
        decrypted_name = crypto.decrypt(encrypted_name)
        
        encrypted_lastname = result.real_last_name
        decrypted_lastname = crypto.decrypt(encrypted_lastname)
        
        # Umwandlung der Abfrageergebnisse in ein Dictionary
        alerts_dict = []
        for alert in alerts:
            alert_data = {
                "id": alert.id,
                "name": decrypted_name,  # Entschlüsselter Name
                "lastname": decrypted_lastname,  # Entschlüsselter Nachname
                "symptom": alert.symptom,
                "medic": alert.medic,
                "timestamp": alert.Alarm_recieved  # Beispiel für ein weiteres Attribut
            }
            alerts_dict.append(alert_data)
        
        print(alerts_dict)
        return alerts_dict
    else:
        return None
def find_real_name(pseudonym):
    """Findet den echten Namen eines Patienten anhand seines Pseudonyms.


    Parameters
    ----------
    pseudonym : str
        Das Pseudonym des Patienten.

    Returns
    -------
    str
        Der echte Name des Patienten.
    """
    
    result = session.query(Pseudonymization).filter_by(pseudonym=pseudonym).first()
    if result is not None:
        encrypted_name = result.real_name
        decrypted_name = crypto.decrypt(encrypted_name)
        return decrypted_name
    else:
        return None 
    
def find_real_lastname(pseudonym):
    result = session.query(Pseudonymization).filter_by(pseudonym=pseudonym).first()
    if result is not None:
        encrypted_lastname = result.real_last_name
        decrypted_lastname = crypto.decrypt(encrypted_lastname)
        return decrypted_lastname
    else:
        return None

def get_all_active_alerts():
    alerts = session.query(Alarmierungen).filter_by(status="aktive").all()
    alerts_dict = []
    for alert in alerts:
        name = find_real_name(alert.name)
        last_name = find_real_lastname(alert.lastname)
        allert_data = {
            "id": alert.id,
            "name": name,
            "lastname": last_name,
            "symptom": alert.symptom,
            "timestamp": alert.Alarm_recieved
        }
        alerts_dict.append(allert_data)
        print(alerts_dict)
    return alerts_dict


def add_health_data(alert_id, pulse, spo2, blood_pressure, temperature, blood_suger, pain):
    alert = session.query(Alarmierungen).filter_by(id=alert_id).first()
    alert.pulse = pulse
    alert.spo2 = spo2
    alert.blood_pressure = blood_pressure
    alert.temperature = temperature
    alert.blood_suger = blood_suger
    alert.pain = pain
    
    session.commit()
def set_alert_status(alert_id, status):
    alert = session.query(Alarmierungen).filter_by(id=alert_id).first()
    alert.status = status
    session.commit()

def add_alert_data(alert_id, teacher, measures, sanitaeter):
    alerts = session.query(Alarmierungen).filter_by(id=alert_id).all()
    print(f"Gefundene Alarme: {alerts}")
    if len(alerts) > 1:
        print("❗ Fehler: Mehrere Alarme mit derselben ID gefunden!")
    alert = alerts[0] if alerts else None
    if alert:
        alert.teacher = teacher
        alert.measures = measures
        alert.medic = sanitaeter
        session.commit()
    else:
        print(f"⚠️ Kein Alarm mit ID {alert_id} gefunden.")

def add_accsess_key(firstname, lastname, key, premission):
    medic = session.query(Medics).filter_by(name=firstname, last_name=lastname).first()
    if not medic:
        medic = Medics(name=firstname, last_name=lastname, premission=premission)
        session.add(medic)
        session.commit()
    medic.karten_nummer = key
    session.commit()

def delete_accsess_key(firstname, lastname):
    medic = session.query(Medics).filter_by(name=firstname, last_name=lastname).first()
    medic.karten_nummer = None
    session.commit()

def check_accsess_premission(key):
    medic = session.query(Medics).filter_by(karten_nummer=key).first()
    if medic is not None:
        return True
    else:
        return False
def check_premission(firstname, lastname):
    medic = session.query(Medics).filter_by(name=firstname, last_name=lastname).first()
    if medic is not None:
        return medic.premission
    else:
        return None
def get_key_name(key):
    medic = session.query(Medics).filter_by(karten_nummer=key).first()
    if medic is not None:
        return f"{medic.name} {medic.last_name}"
    else:
        return None

def add_user(name, last_name, lernbegleiter, premission):
    user = Medics(name=name, last_name=last_name, lernbegleiter=lernbegleiter, premission=premission)
    session.add(user)
    session.commit()

def delete_user(name, last_name):
    user = session.query(Medics).filter_by(name=name, last_name=last_name).first()
    session.delete(user)
    session.commit()

def add_el_data(alert_id, abhol_massnahme, parrents_notified_at, parrents_notified_by, hospital):
    alert = session.query(Alarmierungen).filter_by(id=alert_id).first()
    alert.parrents_notified_at = parrents_notified_at
    alert.abhol_maßnahme = abhol_massnahme
    alert.parrents_notified_by = parrents_notified_by
    alert.hospital = hospital
    session.commit()