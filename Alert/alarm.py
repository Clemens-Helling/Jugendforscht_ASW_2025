import requests
import Data.alerts_crud as database

error = ""


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
        alert_id = database.add_alert(symtom, alert_type )
        print(f"Alert ID in alarm {alert_id}")
        requests.post(
            "https://ntfy.sh/Rfaond6DyhQPMo8P", data=symtom.encode(encoding="utf-8")
               )
        return alert_id
