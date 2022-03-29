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
            print("Handling: "+city)
            if city not in cities:
                cities[city] = [row["plz"]]
            elif city in cities:
                cities[city].append(row["plz"])
            if plz not in plzs: 
                plzs[plz] = row["ort"]
            elif plz in plzs:
                print("Duplicate? : "+plz)




with open(join(current_location, "files/cities_to_plz.json"), "w") as f:
    f.write(json.dumps(cities))

with open(join(current_location, "files/plzs_to_cities.json"), "w") as f:
    f.write(json.dumps(plzs))