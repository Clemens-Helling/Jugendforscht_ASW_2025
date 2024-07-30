import json
import time
import json
import time
from database import insert_alarm
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
    # Convert the JSON data back to a dictionary
    data_dict = json.loads(json_data)

    # Access the values using the keys
    erkranung_value = data_dict["erkranung"]
    timestamp_value = data_dict["timestamp"]

    
    print(f"Alarm: {erkranung_value} at {timestamp_value}")    
   

    return json_data

