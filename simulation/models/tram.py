from .tram_stop import TramStop


class Tram:
    def __init__(self, id: int, current_stop: int, stops: list[int], time_table: list[int], delay: int = 0, route_id: int = 0, passengers: int = 0) -> None:
        self.id = id
        self.current_stop = current_stop
        self.stops = stops
        self.time_table = time_table
        self.delay = delay

        self.passengers = passengers
        self.max_passengers = 300

        self.route_id = route_id

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "current_stop": self.current_stop,
            "stops": self.stops,
            "time_table": self.time_table,
            "delay": self.delay,
            "passengers": self.passengers,
            "route_id": self.route_id
        }
    
    def __str__(self) -> str:
        return f"Tram(id={self.id}, current_stop={self.current_stop}, stops={self.stops}, time_table={self.time_table}, delay={self.delay}, passengers={self.passengers}, route_id={self.route_id})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tram):
            return self.id == other.id
        return False
