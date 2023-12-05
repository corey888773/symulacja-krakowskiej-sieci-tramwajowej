class Edge:
    def __init__(self, id: int, length: float, max_speed: int, nodes: list):
        self.id = id
        self.length = length
        self.max_speed = max_speed
        self.nodes = nodes
        # self.head = head
        # self.tail = tail

    # def to_json(self):
    #     return {
    #         'id': self.id,
    #         'length': self.length,
    #         'max_speed': self.max_speed,
    #         'head': self.head,
    #         'tail': self.tail
    #     }

    # def __str__(self):
    #     return f'Edge(id={self.id}, length={self.length}, max_speed={self.max_speed}, head={self.head}, tail={self.tail})'