import database
error =""
def alarm(erkranung):
    if erkranung == "Wählen Sie eine Krankheit":
        print("keine Krankheit ausgewählt")	
        return("keine Krankheit ausgewählt")
    else: 
        print("Alarm wurde ausgelöst")
        database.insert_alarm(erkranung)

       