import json

def alarm(erkranung):
    if erkranung == "Wählen Sie eine Krankheit" and not "Unklare " and not erkranung.startswith("Sonstiges"):
        return "keine Krankheit ausgewählt"
      