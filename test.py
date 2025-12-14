from db_api.Station import Station
import datetime
import requests
import importlib.resources
import csv
import xmltodict

def get_evano_from_name(name):
    with importlib.resources.path('db_api', 'Bahnhoefe.csv') as path:
        with open(path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                if name.lower() in row['NAME'].lower():
                    return row['EVA_NR']


headers = {
            "DB-Client-Id": "529fc99d86062cff082818f1820c4900",
            "DB-Api-Key": "ef252166427b5094f093b9e5f331508c",
            "accept": "application/xml"
        }

evano = get_evano_from_name("Berlin Hbf")

new_date = datetime.datetime.now().strftime("%y%m%d")
new_hour = datetime.datetime.now().strftime("%H")

url = f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/plan/{evano}/{new_date}/{new_hour}"

response = requests.get(url, headers=headers)
response_json = xmltodict.parse(response.text)
print(response_json)