import json
from datetime import datetime

class Train:
    def __init__(self, station_name, arrival_planned, arrival_actual, departure_planned, departure_actual, platform_planned, platform_actual, canceled, train_number, train_type, train_line, train_id, past_destinations, future_destinations):
        self.station_name = station_name
        self.past_destinations = past_destinations
        self.future_destinations = future_destinations
        self.arrival_planned = datetime.strptime(arrival_planned, "%y%m%d%H%M") if arrival_planned else None
        self.arrival_actual = datetime.strptime(arrival_actual, "%y%m%d%H%M") if arrival_actual else None
        self.departure_planned = datetime.strptime(departure_planned, "%y%m%d%H%M") if departure_planned else None
        self.departure_actual = datetime.strptime(departure_actual, "%y%m%d%H%M") if departure_actual else None
        self.platform_planned = platform_planned
        self.platform_actual = platform_actual
        self.canceled = canceled
        self.train_number = train_number
        self.train_type = train_type
        self.train_line = train_line
        self.train_id = train_id
        self.platform_change = False if platform_actual == None else True
        self.final_destination = self.future_destinations.split('|')[-1] if self.future_destinations else self.station_name
        self.start_station = self.past_destinations.split('|')[0] if self.past_destinations else self.station_name
        if self.departure_actual != None and self.departure_planned != None:
            delay_time = self.departure_actual - self.departure_planned
            self.delay = int(delay_time.total_seconds() // 60)
        elif self.arrival_actual != None and self.arrival_planned != None:
            delay_time = self.arrival_actual - self.arrival_planned
            self.delay = int(delay_time.total_seconds() // 60)
        else:
            self.delay = None

    def print_train(self):
        print(f"Station Name: {self.station_name}")
        print(f"Train ID: {self.train_id}")
        print(f"Train Number: {self.train_number}")
        print(f"Final Destination: {self.final_destination}")
        print(f"Start Station: {self.start_station}")
        print(f"Train Type: {self.train_type}")
        print(f"Past Destinations: {self.past_destinations}")
        print(f"Future Destinations: {self.future_destinations}")
        print(f"Canceled: {self.canceled}")
        print(f"Arrival Planned: {self.arrival_planned}")
        print(f"Arrival Actual: {self.arrival_actual}")
        print(f"Departure Planned: {self.departure_planned}")
        print(f"Departure Actual: {self.departure_actual}")
        print(f"Platform Planned: {self.platform_planned}")
        print(f"Platform Actual: {self.platform_actual}")
        print(f"Train Line: {self.train_line}")
        print(f"Delay: {self.delay}")
        print("\n")
        
    def get_station_name(self):
        return self.station_name
    
    def get_train_id(self):
        return self.train_id
    
    def get_arrival_planned(self):
        return self.arrival_planned

    def get_arrival_actual(self):
        return self.arrival_actual

    def get_departure_planned(self):
        return self.departure_planned

    def get_departure_actual(self):
        return self.departure_actual

    def get_platform_planned(self):
        return self.platform_planned

    def get_platform_actual(self):
        return self.platform_actual

    def get_canceled(self):
        return self.canceled

    def get_train_number(self):
        return self.train_number

    def get_train_type(self):
        return self.train_type

    def get_train_category(self):
        return self.train_line

    def get_past_destinations(self):
        return self.past_destinations

    def get_future_destinations(self):
        return self.future_destinations

    def get_platform_change(self):
        return self.platform_change

    def get_final_destination(self):
        return self.final_destination

    def get_start_station(self):
        return self.start_station
    
    def get_delay(self):
        return self.delay