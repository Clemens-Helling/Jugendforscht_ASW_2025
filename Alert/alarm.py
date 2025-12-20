import requests
import os
import json
import Data.alerts_crud as database
from Data.settings_crud import get_user_settings
from easy_logger.easy_logger import EasyLogger

logger = EasyLogger(
    name="AlarmModule",
    level="INFO",
    log_to_file=True,
    log_to_console=False,
    log_dir="logs",
    log_file="alarm.log")
error = ""

user_settings = get_user_settings(1)


divera_accesskey = user_settings["divera_key"]
divera_ric = user_settings.get("divera_ric", "SaniLink")
divera_api_url = "https://www.divera247.com/api/alarm"
ntfy_url = user_settings["ntfy_url"]
method = user_settings["method"]

def add_alert(symtom, alert_type):
    """Löst einen Alarm aus, wenn ein Symptom ausgewählt wurde und fügt den Alarm zur Datenbank hinzu.

    Parameters
    ----------
    symtom : str
        Symptom, das ausgewählt wurde.
    name : str
        Name des Patienten.
    last_name : str
        Nachname des Patienten.
    """
    if symtom == "Wählen Sie eine Krankheit":
        print("keine Krankheit ausgewählt")
        return "keine Krankheit ausgewählt"
    else:
        send_alert(symtom)
        print("Alarm wurde ausgelöst")
        alert_id = database.add_alert(symtom, alert_type)
        print(f"Alert ID in alarm {alert_id}")
        print(f"Method: {method}")

        return alert_id

def add_material_alert(material_name, alert_type):
    """Löst einen Alarm aus, wenn der Materialbestand niedrig ist und fügt den Alarm zur Datenbank hinzu.

    Parameters
    ----------
    material_name : str
        Name des Materials.
    """
    print("Material Alarm wurde ausgelöst")
    alert_id = database.add_material_alert(material_name, alert_type)
    print(f"Alert ID in alarm {alert_id}")
    message = f"Niedriger Bestand: {material_name}"
    requests.post(
        "https://www.divera247.com/api/alarm?accesskey=_h4Gk6GtrGo5jU6PocoxHsnWD2YNwcbnccKDQA2qFI8x0XwbGIyaA3Uri_tKjh-v",

    )
    return alert_id


def send_message(message):
    """Sendet eine Nachricht an den NTFY-Dienst.

    Parameters
    ----------
    message : str
        Nachricht, die gesendet werden soll.
    """
    requests.post(
        "https://ntfy.sh/2sISQuW9tQgMpCmS", data=message.encode(encoding="utf-8")
    )
    print("Nachricht gesendet")
def send_alert(message):
    if method == "Option 1":
        logger.info("Divera Alarm wird gesendet")
        print("Divera Alarm wird gesendet")
        requests.post(
            divera_api_url,
            params={"accesskey": divera_accesskey},
            data={"type": message, "priority": "high", "ric": divera_ric}
        )
        logger.info("Alarm wird gesendet")
    else:  # ntfy
        logger.info("NTFY Alarm wird gesendet")
        print("NTFY Alarm wird gesendet")
        requests.post(
            ntfy_url, data=f"Neuer Alarm: {message}".encode(encoding="utf-8")
        )

if __name__ == "__main__":
    requests.post(
        divera_api_url,
        params={"accesskey": divera_accesskey},
        data={"type": "Tset", "priority": "high", "ric": divera_ric}
    )