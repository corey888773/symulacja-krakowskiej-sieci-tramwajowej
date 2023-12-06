from .node import Node

class TramStop(Node):
    def __init__(self, id: int, x: float, y: float, stop_name: str, generation_distribution: list[int]) -> None:
        super().__init__(id, x, y)
        self.stop_name = stop_name
        self.generation_distribution = generation_distribution

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "stop_name": self.stop_name,
            "generation_distribution": self.generation_distribution
        }

    def __str__(self) -> str:
        return f"TramStop(id={self.id}, x={self.x}, y={self.y}, stop_name={self.stop_name}, generation_distribution={self.generation_distribution})"