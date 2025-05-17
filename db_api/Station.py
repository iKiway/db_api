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
        path = importlib.resources.path('db_api', 'Bahnhoefe.csv')
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
        for i in range(num_hours):
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
    
    def get_train_data(self, date=datetime.now().strftime("%y%m%d"), hour=datetime.now().strftime("%H"), num_hours = 1):
        train_list = []
        
        planned_data = self.send_request_planned_many(date, hour, num_hours)
        delay_data = self.send_request_delay()
        if planned_data is not None:
            station_name = planned_data["timetable"]["@station"]
            
            for train_data in planned_data["timetable"]["s"]:
                train_id = train_data["@id"]
                
                train_type = train_data["tl"]["@c"]
                train_number = train_data["tl"]["@n"]
                if 'ar' in train_data.keys():
                    arrival_planned = train_data["ar"]["@pt"]
                    platform_planned = train_data["ar"]["@pp"]
                    train_line = train_data["ar"].get("@l", None)
                    past_destinations = train_data["ar"].get("@ppth", None)
                else:
                    arrival_planned = None
                    platform_planned = None
                    train_line = None
                    past_destinations = None
                if 'dp' in train_data.keys():
                    departure_planned = train_data["dp"]["@pt"]
                    platform_planned = train_data["dp"]["@pp"]
                    train_line = train_data["dp"].get("@l", None)
                    future_destinations = train_data["dp"].get("@ppth", None)
                else:
                    departure_planned = None
                    future_destinations = None
                    
                for train_delay in (delay_data or {}).get("timetable", {}).get("s", []):
                    if train_id == train_delay["@id"]:
                        arrival_actual = train_delay.get("ar", {}).get("@ct", None)
                        departure_actual = train_delay.get("dp", {}).get("@ct", None)
                        platform_actual = train_delay.get("ar", {}).get("@pp", None)
                        if platform_actual is None:
                            platform_actual = train_delay.get("dp", {}).get("@pp", None)
                        

                        m_list = train_delay.get("dp", {}).get("m", [])
                        if m_list is []:
                            m_list = train_delay.get("ar", {}).get("m", [])

                        if train_delay.get("ar", {}).get("@cs") == "c" or train_delay.get("dp", {}).get("@cs") == "c":
                            canceled = True
                            # print(train_delay)
                        else:
                            canceled = False
                        break
                else:
                    arrival_actual = None
                    departure_actual = None
                    platform_actual = None
                    canceled = False
                        
                
                train = Train(station_name, arrival_planned, arrival_actual, departure_planned, departure_actual, platform_planned, platform_actual, canceled, train_number, train_type, train_line, train_id, past_destinations, future_destinations)
                train_list.append(train)
        else:
            train_list = []

        return train_list
    
    def get_sorted_departure_list(self, delay=True, date=datetime.now().strftime("%y%m%d"), hour=datetime.now().strftime("%H"), time_flag = int(datetime.now().strftime("%y%m%d%H%M")), num_hours = 1):
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
        sorted_trains = [
            zug for zug in sorted_trains
            if (int(zug.departure_actual.strftime("%y%m%d%H%M")) if zug.departure_actual is not None else int(zug.departure_planned.strftime("%y%m%d%H%M"))) >= time_flag
        ]
        return sorted_trains
    

