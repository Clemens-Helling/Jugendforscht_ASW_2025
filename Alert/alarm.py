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
        alert_id = database.add_alert(symtom, alert_type)
        print(f"Alert ID in alarm {alert_id}")
        requests.post(
            "https://ntfy.sh/Rfaond6DyhQPMo8P",
            data=symtom.encode(encoding="utf-8"),
            headers={
                "Title": "Alarm",
                "Priority": "urgent",
                "Tags": "warning",
            },
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
        "https://ntfy.sh/Rfaond6DyhQPMo8P",
        data=message.encode(encoding="utf-8"),
        headers={
            "Title": "Material Alarm",
            "Priority": "urgent",
            "Tags": "warning",
        },
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
