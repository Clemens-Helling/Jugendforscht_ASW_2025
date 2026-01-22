from datetime import UTC, datetime
import os

import pytz
from contextlib import contextmanager
from Data.models import Alarmierung, Protokoll
from Data.setup_database import session
from sqlalchemy import or_
from easy_logger.secure_log_client import SecureLogClient
from easy_logger.error_codes import ErrorCodes

utc_time = datetime.now(UTC)
local_time = utc_time.astimezone(pytz.timezone("Europe/Berlin"))
print(local_time)

# Initialize secure log client
secure_logger = None
if os.path.exists('/home/clemens/dev/Jugendforscht_ASW_2025/keys/client_private_key.pem'):
    try:
        secure_logger = SecureLogClient(
            server_url='http://192.168.178.112:5000',
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

def add_alert(symptom, alert_type):
    alert = Alarmierung(
        symptom=symptom, alert_type=alert_type, alert_received=datetime.now()
    )

    session.add(alert)

    session.flush()
    alert_id = alert.alert_id
    protokoll = Protokoll(alert_id=alert.alert_id, status= "open")
    print(alert.alert_id)

    session.add(protokoll)
    session.commit()

    # WICHTIG: Session expiren nach dem Commit
    session.expire_all()
    
    if secure_logger:
        secure_logger.send_log('INFO', 'New alert created', {'alert_id': alert_id, 'symptom': symptom, 'alert_type': alert_type})

    return alert_id


def get_alerts():
    """Gibt alle Alarmierungen zurück."""
    # Session vor Abfrage refreshen
    session.expire_all()

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


def get_all_active_alerts():
    with session_scope() as s:
        protokolls = s.query(Protokoll).filter(or_(Protokoll.status == "open", Protokoll.status == "ohne Name")).all()
        active_alerts = []
        for protokoll in protokolls:
            alert = (
                s.query(Alarmierung)
                .filter(Alarmierung.alert_id == protokoll.alert_id)
                .first()
            )
            if alert:
                active_alerts.append(
                    {
                        "id": alert.alert_id,
                        "alert_received": alert.alert_received,
                        "alert_type": alert.alert_type,
                        "symptom": alert.symptom,
                    }
                )
        return active_alerts

def get_alert_by_id(alert_id):
    """Gibt eine Alarmierung anhand ihrer ID zurück."""
    alert = session.query(Alarmierung).filter_by(alert_id=alert_id).first()
    if alert:
        if secure_logger:
            secure_logger.send_log('INFO', 'Alert retrieved', {'alert_id': alert_id})
        return {
            "alert_id": alert.alert_id,
            "alert_received": alert.alert_received,
            "alert_type": alert.alert_type,
            "symptom": alert.symptom,
        }
    else:
        if secure_logger:
            secure_logger.send_log('WARNING', 'Alert not found', {'error_code': ErrorCodes.RESOURCE_NOT_FOUND, 'alert_id': alert_id})
        return None