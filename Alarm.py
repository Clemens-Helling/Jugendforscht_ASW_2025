import json
import time
import json
import time
def alarm(erkranung):
    if erkranung == "Wählen Sie eine Krankheit" or erkranung.startswith("Unklare ") or erkranung.startswith("Sonstiges"):
        return False

    # Create a dictionary to store the information
    data = {
        "erkranung": erkranung,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }

    # Convert the dictionary to JSON format
    json_data = json.dumps(data)

    # Do something with the JSON data
    # ...

    return json_data

