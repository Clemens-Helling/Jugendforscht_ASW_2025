import requests
import os
from dotenv import load_dotenv
import Data.alerts_crud as database

error = ""
load_dotenv(dotenv_path=r"C:\Users\cleme\Desktop\JugendForscht\Jugendforscht_ASW_2025\sanilink.env")

# Zugriff auf die Variablen
divera_api_url = os.getenv("DIVERA_API_URL")
divera_accesskey = os.getenv("DIVERA_API_ACCESSKEY")
load_dotenv()
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
        print("Alarm wurde ausgelöst")
        alert_id = database.add_alert(symtom, alert_type)
        print(f"Alert ID in alarm {alert_id}")
        requests.post(
            divera_api_url,
            params={"accesskey": divera_accesskey},
            data={"type": symtom, "priority": "high", "ric": "SaniLink"},
        )
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

