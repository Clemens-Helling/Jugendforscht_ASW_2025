import Data.database as database
import requests
error =""
def alarm(symtom, name, last_name):
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
        return("keine Krankheit ausgewählt")
    else: 
        print("Alarm wurde ausgelöst")
        database.add_alarm(name, last_name, symtom)
        requests.post("https://ntfy.sh/Rfaond6DyhQPMo8P",
                      data=symtom.encode(encoding='utf-8'))