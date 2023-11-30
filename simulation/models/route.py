class Route:
    def __init__(self, route_id: int, start: str, stop: str, route_stops: list[int]) -> None:
        self.id = route_id
        self.start = start
        self.stop = stop 
        self.stops = route_stops

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "start": self.start,
            "stop": self.stop,
            "stops": self.stops
        }

    def __str__(self) -> str:
        return f"Route(id={self.id}, start={self.start}, stop={self.stop}, stops={self.stops})"