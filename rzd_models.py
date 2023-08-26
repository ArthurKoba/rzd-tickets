from dataclasses import dataclass, field
from datetime import datetime, date
from json import dumps


@dataclass(kw_only=True)
class TrainFilter:
    origin: str
    destination: str
    departure_date: date
    time_from: int = field(repr=False, default=0)
    time_to: int = field(repr=False, default=24)
    car_grouping: str = field(repr=False, default="DontGroup")
    get_by_local_time: bool = field(repr=False, default=True)
    special_places_demand: str = field(repr=False, default="StandardPlacesAndForDisabledPersons")
    get_trains_from_schedule: bool = field(repr=False, default=True)

    def get_json_to_request(self):
        return dumps({
            "Origin": self.origin,
            "Destination": self.destination,
            "DepartureDate": self.departure_date.strftime("%Y-%m-%dT00:00:00"),
            "TimeFrom": self.time_from,
            "TimeTo": self.time_to,
            "CarGrouping": self.car_grouping,
            "GetByLocalTime": self.get_by_local_time,
            "SpecialPlacesDemand": self.special_places_demand,
            "GetTrainsFromSchedule": self.get_trains_from_schedule
        })


@dataclass(init=False)
class Car:
    type: str
    price: str
    total_place_quantity: int
    service_class: str

    def __init__(self, **data):
        self.type = data.get("CarTypeName")
        delta_price = int(data.get("MaxPrice", 0) - data.get("MinPrice", 0))
        self.price = f'{int(data.get("MinPrice", 0))}±{delta_price}'
        self.total_place_quantity = data.get("TotalPlaceQuantity", 0)
        self.service_class = data.get("ServiceClasses")
        if type(self.service_class) == list and len(self.service_class) == 1:
            self.service_class = self.service_class[0]
        else:
            self.service_class = str(self.service_class)

    @staticmethod
    def parse_cars(data):
        return [
            Car(**car_data)
            for car_data in data.get("CarGroups", [])
            if car_data.get("CarType") != "Baggage"
        ]


@dataclass(init=False)
class Train:
    number: str
    carrier: str = field(repr=False)
    departure_datetime: datetime
    arrival_datetime: datetime
    origin_station: str
    destination_station: str
    origin_code: str = field(repr=False)
    destination_code: str = field(repr=False)
    cars: list[Car] = field(repr=False)
    total_place_quantity: int

    def __init__(self, **data):
        self.number = data.get("TrainNumber")
        self.carrier = data.get("CarrierDisplayNames")
        self.departure_datetime = datetime.strptime(data.get("DepartureDateTime"), "%Y-%m-%dT%H:%M:%S")
        self.arrival_datetime = datetime.strptime(data.get("ArrivalDateTime"), "%Y-%m-%dT%H:%M:%S")
        if type(self.carrier) == list and len(self.carrier) == 1:
            self.carrier = self.carrier[0]
        else:
            self.carrier = str(self.carrier)
        origin_info = data.get("OriginStationInfo", {})
        self.origin_code = origin_info.get("StationCode")
        self.origin_station = origin_info.get("StationName")
        destination_info = data.get("DestinationStationInfo", {})
        self.destination_station = destination_info.get("StationName")
        self.destination_code = destination_info.get("StationCode")
        self.cars = Car.parse_cars(data)

    def get_datetime(self):
        return self.departure_datetime.strftime("%Y-%m-%d %H:%m")

    @property
    def total_place_quantity(self):
        total_place_quantity = 0
        for car in self.cars:
            total_place_quantity += car.total_place_quantity
        return total_place_quantity

    @staticmethod
    def parse_trains(data):
        return [Train(**train_data) for train_data in data.get("Trains", [])]
