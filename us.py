import json

# 1. Read the JSON file
with open("./city.list.json", "r") as file:
    data = json.load(file)

# 2. Filter objects where country == "US"
us_cities = [city for city in data if city["country"] == "US"]

# us_cities now contains all objects with country value == "US"

# If you wish to write the filtered data back to a new JSON file:
with open("us_cities.json", "w") as file:
    json.dump(us_cities, file, indent=4)
