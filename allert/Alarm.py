from data.database import insert_alarm
error =""
def alarm(erkranung):
    if erkranung == "Wählen Sie eine Krankheit":
        error = "keine Krankheit ausgewählt"
    else: insert_alarm(erkranung)
    
       