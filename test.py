import json
name = "Claudia"
data = {
    "name": name,
    "age": 30,
    "city": "New York",
    "einkaeufe": ["Brokoli", "Milch"]

}
json_data = json.dumps(data, indent=4)
print(json_data)