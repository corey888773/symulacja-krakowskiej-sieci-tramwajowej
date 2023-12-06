from .tram_stop import TramStop

class Tram:
    def __init__(self, id: int, current_stop: TramStop, stops: list[TramStop], time_table: list[int]) -> None:
        self.id = id
        self.current_stop = current_stop
        self.stops = stops
        self.time_table = time_table

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "current_stop": self.current_stop,
            "stops": self.stops,
            "time_table": self.time_table
        }
    
    def __str__(self) -> str:
        return f"Tram(id={self.id}, current_stop={self.current_stop}, stops={self.stops}, time_table={self.time_table})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tram):
            return self.id == other.id
        return False