from Data.setup_database import session
from Data.models import Alarmierung, Protokoll
from datetime import datetime, UTC
import pytz

utc_time = datetime.now(UTC)
local_time = utc_time.astimezone(pytz.timezone('Europe/Berlin'))
print(local_time)
def add_alert(symptom, alert_type):
    alert = Alarmierung(
        symptom=symptom, alert_type=alert_type, alert_received=datetime.datetime.now()
    )

    session.add(alert)

    session.flush()
    alert_id = alert.alert_id
    protokoll = Protokoll(alert_id=alert.alert_id)
    print(alert.alert_id)

    session.add(protokoll)
    session.commit()
    return alert_id


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
