import database
error =""
def alarm(symtom, name, last_name):
    if symtom == "Wählen Sie eine Krankheit":
        print("keine Krankheit ausgewählt")	
        return("keine Krankheit ausgewählt")
    else: 
        print("Alarm wurde ausgelöst")
        database.add_alarm(name, last_name, symtom)
       