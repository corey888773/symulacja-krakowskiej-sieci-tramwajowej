class Trip:
    def __init__(self, route_id: int, time_table: list[int], generation_left: list[int], absorption_left: list[int]) -> None:
        self.route_id = route_id
        self.time_table = time_table

        self.generation_left = generation_left
        self.absorption_left = absorption_left

    def to_json(self) -> dict:
        return {
            "route_id": self.route_id,
            "time_table": self.time_table,
            "generation_left": self.generation_left,
            "absorption_left": self.absorption_left
        }
    
    def __str__(self) -> str:
        return f"Trip(route_id={self.route_id}, time_table={self.time_table}, generation_left={self.generation_left}, absorption_left={self.absorption_left})"