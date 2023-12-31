REMOVED_STOPS = [
    'KrowodrzaGórkaP+R03',
]

class Stop:
    def __init__(self, raw_stop : dict):
        self.name = raw_stop['name'].strip().replace(' ', '')
        self.schedule = self.prepare_schedule(raw_stop['schedule'][0])
        self.is_removed = False

        if self.name in REMOVED_STOPS:
            self.is_removed = True
        
    def prepare_schedule(self, raw_schedule : list):
        last_hour_idx = None
        for idx, times in enumerate(raw_schedule[1:]):
            if times[0].isdigit() == False:
                last_hour_idx = idx
                break

        return raw_schedule[1:last_hour_idx]


class Direction:
    def __init__(self, raw_direction : dict):
        self.name = raw_direction['name'].strip().replace(' ', '')

        temp_stops = [Stop(raw_stop) for raw_stop in raw_direction['stops']]
        self.stops = [stop for stop in temp_stops if not stop.is_removed]


class Line:
    def __init__(self, raw_line : dict):
        self.number = raw_line['number']
        self.direction1 = Direction(raw_line['direction1'])
        self.direction2 = Direction(raw_line['direction2'])


class Schedule:
    def __init__(self, main_schedule : dict):
        self.lines = [Line(raw_line) for raw_line in main_schedule['lines']]


