import importlib.resources
import os
import requests
import json
import datetime
import xmltodict
import csv
from .Train import Train
from datetime import datetime, timedelta

class Station:
    def __init__(self, name, db_client_id, db_api_key):
        self.name = name
        self.evano = self.get_evano_from_name(name)
        self.headers = {
            "DB-Client-Id": db_client_id,
            "DB-Api-Key": db_api_key,
            "accept": "application/xml"
        }

    def __str__(self):
        return json.dumps(self.station_data, indent=2, ensure_ascii=False)
    
    def get_evano_from_name(self, name):
        with importlib.resources.path('db_api', 'Bahnhoefe.csv') as path:
            with open(path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    if name.lower() in row['NAME'].lower():
                        return row['EVA_NR']
        return None
    
    def get_evano(self):
        return self.evano
    
    def send_request_planned(self, date, hour):
        url = f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/plan/{self.evano}/{date}/{hour}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return xmltodict.parse(response.text)
        else:
            print(f"Error: {response.status_code}")
            return None
        
        
    def send_request_planned_many(self, date, hour, num_hours = 1):
        full_response = None
        for i in range(-5, num_hours):
            dt = datetime.strptime(date + hour, "%y%m%d%H")
            dt_plus1 = dt + timedelta(hours=i)
            new_date = dt_plus1.strftime("%y%m%d")
            new_hour = dt_plus1.strftime("%H")
            url = f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/plan/{self.evano}/{new_date}/{new_hour}"
            
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                response_json = xmltodict.parse(response.text)
                if isinstance(response_json.get("timetable"), dict) and response_json["timetable"].get("s", None) is not None:

                    if not isinstance(response_json["timetable"]["s"], list):
                            response_json["timetable"]["s"] = [response_json["timetable"]["s"]]
                    if full_response is None:
                        full_response = response_json
                    else:
                        if isinstance(full_response, dict) and isinstance(response_json, dict):
                            full_response["timetable"]["s"].extend(response_json["timetable"]["s"])
                        else:
                            print("Error: Merging responses failed.")

            else:
                print(f"Error: {response.status_code}")
        
        return full_response

            
    
    def send_request_delay(self):
        url_delay = f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/fchg/{self.evano}"
        response_delay = requests.get(url_delay, headers=self.headers)
        if response_delay.status_code == 200:
            return xmltodict.parse(response_delay.text)
        else:
            print(f"Error: {response_delay.status_code}")
            return None
        
    def get_delay_data(self):
        delay_data = self.send_request_delay()
        if delay_data is not None:
            station_name = delay_data["timetable"]["@station"]
            train_list = []
            for train_data in delay_data["timetable"]["s"]:
                train_id = train_data["@id"]
                arrival_actual = train_data.get("ar", {}).get("@ct", None)
                departure_actual = train_data.get("dp", {}).get("@ct", None)
                platform_actual = train_data.get("ar", {}).get("@pp", None) or train_data.get("dp", {}).get("@pp", None)
                
                if train_data.get("ar", {}).get("@cs") == "c" or train_data.get("dp", {}).get("@cs") == "c":
                    canceled = True
                else:
                    canceled = False
                
                train = Train(station_name, None, arrival_actual, None, departure_actual, None, platform_actual, canceled, None, None, None, train_id, None, None)
                train_list.append(train)
            return train_list
        else:
            return []
        
    
    def get_train_data(self, date=datetime.now().strftime("%y%m%d"), hour=datetime.now().strftime("%H"), num_hours = 1):
        train_list = []
        
        planned_data = self.send_request_planned_many(date, hour, num_hours)
        delay_data = self.send_request_delay()
        delay_list = (delay_data or {}).get("timetable", {}).get("s", [])
        
        print(f"Found {len(delay_list)} trains with delay data.")
        if planned_data is not None:
            station_name = planned_data["timetable"]["@station"]
            
            for train_data in planned_data["timetable"]["s"]:
                train_id = train_data["@id"]
                
                category = train_data["tl"]["@c"]
                train_number = train_data["tl"]["@n"]
                if 'ar' in train_data.keys():
                    arrival_planned = train_data["ar"]["@pt"]
                    platform_planned = train_data["ar"]["@pp"]
                    line_name = train_data["ar"].get("@l", None)
                    past_destinations = train_data["ar"].get("@ppth", None)
                else:
                    arrival_planned = None
                    platform_planned = None
                    line_name = None
                    past_destinations = None
                if 'dp' in train_data.keys():
                    departure_planned = train_data["dp"]["@pt"]
                    platform_planned = train_data["dp"]["@pp"]
                    line_name = train_data["dp"].get("@l", None)
                    future_destinations = train_data["dp"].get("@ppth", None)
                else:
                    departure_planned = None
                    future_destinations = None
                    
                for idx, train_delay in enumerate(delay_list):
                    if train_id == train_delay["@id"]:
                        arrival_actual = train_delay.get("ar", {}).get("@ct", None)
                        departure_actual = train_delay.get("dp", {}).get("@ct", None)
                        platform_actual = train_delay.get("ar", {}).get("@pp", None)
                        if platform_actual is None:
                            platform_actual = train_delay.get("dp", {}).get("@pp", None)

                        if train_delay.get("ar", {}).get("@cs") == "c" or train_delay.get("dp", {}).get("@cs") == "c":
                            canceled = True
                        else:
                            canceled = False
                        del delay_list[idx]
                        break

                else:
                    arrival_actual = None
                    departure_actual = None
                    platform_actual = None
                    canceled = False
                        
                
                train = Train(station_name, arrival_planned, arrival_actual, departure_planned, departure_actual, platform_planned, platform_actual, canceled, train_number, category, line_name, train_id, past_destinations, future_destinations)
                train_list.append(train)

            if delay_list:
                for train_delay in delay_list:
                    if train_delay.get("ar", {}).get("@pt", None) is not None and train_delay.get("dp", {}).get("@pt", None) is not None and train_delay.get("tl", {}).get("@c", None) is not None:
                        arrival_planned = train_delay.get("ar", {}).get("@pt", None)
                        departure_planned = train_delay.get("dp", {}).get("@pt", None)
                        platform_planned = train_delay.get("ar", {}).get("@pp", None)
                        arrival_actual = train_delay.get("ar", {}).get("@ct", None)
                        departure_actual = train_delay.get("dp", {}).get("@ct", None)
                        platform_actual = train_delay.get("ar", {}).get("@pp", None)
                        train_number = train_delay.get("tl", {}).get("@n", None)
                        category = train_delay.get("tl", {}).get("@c", None)
                        line_name = train_delay.get("ar", {}).get("@l", None) or train_delay.get("dp", {}).get("@l", None)
                        train = Train(station_name, arrival_planned, arrival_actual, departure_planned, departure_actual, platform_planned, platform_actual, canceled, train_number, category, line_name, train_id, past_destinations, future_destinations)
                        train_list.append(train)

            if delay_list:
                print(len(delay_list), "Trains with delay not found in planned data.")
            else:
                print("No planned data found for the given date and hour.")
            
        else:
            train_list = []

        return train_list
    
    def get_sorted_departure_list(self, delay=True, date=datetime.now().strftime("%y%m%d"), hour=datetime.now().strftime("%H"), time_flag = int(datetime.now().strftime("%y%m%d%H%M")), num_hours = 1, filterByDirection = False, direction = ""):
        train_list = self.get_train_data(date, hour, num_hours)
        train_list = [train for train in train_list if train.departure_planned is not None]
        if delay:
            sorted_trains = sorted(
                train_list, 
                key=lambda train: int(train.departure_actual.strftime("%y%m%d%H%M")) if train.departure_actual is not None else int(train.departure_planned.strftime("%y%m%d%H%M"))
            )
        else:
            sorted_trains = sorted(
                train_list, 
                key=lambda train: int(train.departure_planned.strftime("%y%m%d%H%M"))
            )
        if filterByDirection:
            # direction kann ein String, JSON-String oder eine Liste sein
            if isinstance(direction, str):
                # Versuche JSON zu parsen, falls es ein JSON-String ist
                if direction.strip().startswith('['):
                    try:
                        directions = json.loads(direction)
                    except json.JSONDecodeError:
                        directions = [direction] if direction != "" else []
                else:
                    directions = [direction] if direction != "" else []
            elif isinstance(direction, list):
                directions = direction
            else:
                directions = []
            
            if directions:
                sorted_trains = [
                    zug for zug in sorted_trains
                    if zug.future_destinations is not None and any(
                        dir.strip().lower() in [dest.strip().lower() for dest in zug.future_destinations.split('|')]
                        for dir in directions
                    )
                ]
        sorted_trains = [
            zug for zug in sorted_trains
            if (int(zug.departure_actual.strftime("%y%m%d%H%M")) if zug.departure_actual is not None else int(zug.departure_planned.strftime("%y%m%d%H%M"))) >= time_flag
        ]
        return sorted_trains
    

