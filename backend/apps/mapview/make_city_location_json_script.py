import json
from os.path import dirname, abspath, join
import csv

cities = {}
plzs = {}
current_location = dirname(abspath(__file__))
from os.path import join

for countrycode in ["DE", "AT"]:
    with open(join(current_location, f'files/{countrycode}.csv'), encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = row["ort"]
            plz = row["plz"]
            if city not in cities:
                cities[city] = [{"lat" : row["lat"], "lon" : row["lon"]}]
            elif city in cities:
                cities[city].append({"lat" : row["lat"], "lon" : row["lon"]})

print("Done aggregating, now reading json and calculating average center for all cities with multiple entries.")
cleanCities = {}
for city in cities: 
    avgLat = 0
    avgLon = 0
    for entry in cities[city]: 
        print(str(entry))
        if entry["lat"] != " " and entry["lon"] != " ":
            avgLat += float(entry["lat"])
            avgLon += float(entry["lon"])
    cleanCity = [avgLat/len(cities[city]), avgLon/len(cities[city])]
    cleanCities[city] = cleanCity

with open(join(current_location, "files/cities_to_center.json"), "w") as f:
    f.write(json.dumps(cleanCities))
