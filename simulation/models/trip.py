class Trip:
    def __init__(self, route_id: int, time_table: list[int]) -> None:
        self.route_id = route_id
        self.time_table = time_table

    def to_json(self) -> dict:
        return {
            "route_id": self.route_id,
            "time_table": self.time_table
        }
    
    def __str__(self) -> str:
        return f"Trip(route_id={self.route_id}, time_table={self.time_table})"