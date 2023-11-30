class Node:
    def __init__(self, id: int, x: float, y: float, ) -> None:
        self.id = id
        self.x = x
        self.y = y

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y
        }

    def __str__(self) -> str:
        return f"Node({self.id}, {self.x}, {self.y})"