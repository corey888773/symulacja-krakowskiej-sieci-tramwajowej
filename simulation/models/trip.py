class Trip:
    def __init__(self, route: int, time_table: list[int]) -> None:
        self.route = route
        self.time_table = time_table

    def to_json(self) -> dict:
        return {
            "route": self.route,
            "time_table": self.time_table
        }
    
    def __str__(self) -> str:
        return f"Trip(route_id={self.route}, time_table={self.time_table})"