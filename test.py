from allert.Alarm import alarm
erkranung = "test"
if alarm(erkranung) == "keine Krankheit ausgewählt":
    print("Test erfolgreich")
else:
    print("Test fehlgeschlagen")
