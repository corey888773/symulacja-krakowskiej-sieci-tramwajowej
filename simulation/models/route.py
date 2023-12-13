class Route:
    def __init__(self, id: int, start: str, stop: str, stops: list[int], line: int) -> None:
        self.id = id
        self.start = start
        self.stop = stop 
        self.stops = stops
        self.line = line

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "start": self.start,
            "stop": self.stop,
            "stops": self.stops,
            "line": self.line
        }

    def __str__(self) -> str:
        return f"Route(id={self.id}, start={self.start}, stop={self.stop}, stops={self.stops}, line={self.line})"