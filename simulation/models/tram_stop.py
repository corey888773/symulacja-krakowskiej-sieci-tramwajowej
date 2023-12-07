from .node import Node

class TramStop(Node):
    def __init__(self, id: int, x: float, y: float, stop_name: str, generation_rate: list[int], absorption_rate: list[int]) -> None:
        super().__init__(id, x, y)
        self.stop_name = stop_name
        self.generation_rate = generation_rate
        self.absorption_rate = absorption_rate

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "stop_name": self.stop_name,
            "generation_rate": self.generation_rate,
            "absorption_rate": self.absorption_rate
        }

    def __str__(self) -> str:
        return f"TramStop(id={self.id}, x={self.x}, y={self.y}, stop_name={self.stop_name}, generation_rate={self.generation_rate}, absorption_rate={self.absorption_rate})"