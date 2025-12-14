from db_api.Station import Station
from datetime import datetime

try:
    station = Station("mannheim Hbf","529fc99d86062cff082818f1820c4900","ef252166427b5094f093b9e5f331508c")
except:
    station = None

train_list = station.get_sorted_departure_list(num_hours=0)
# train_list = station.get_delay_data()
print(len(train_list))
for train in train_list:
    train.print_train()
    print(train.get_station_name())
    departure = train.get_departure_planned()
    print(train.get_departure_planned())
    # print(datetime.datetime.strptime(departure, "%y%m%d%H%M").strftime("%H:%M"))
    print(train_list[0:10])
    print(len(train_list))
    print(train.get_delay())
    
# print(station.send_request_delay())
# print(station.send_request_planned_many(date=datetime.now().strftime("%y%m%d"), hour=datetime.now().strftime("%H"), num_hours = 1))

with open("delay_response.txt", "w", encoding="utf-8") as f:
    f.write(str(station.send_request_delay()))