class Schedule:
    def __init__(self, main_schedule : dict):
        self.lines = self.pretify_lines(main_schedule)

    def pretify_lines(self, main_schedule : dict) -> list:
        for line in main_schedule['lines']:
            line['number'] = line['number'].strip()
            line['direction1']['name'] = line['direction1']['name'].strip()
            line['direction2']['name'] = line['direction2']['name'].strip()

            for stop in line['direction1']['stops']:
                stop['name'] = stop['name'].strip()

                last_hour_idx = None
                for idx, times in enumerate(stop['schedule'][0][1:]):
                    if times[0].isdigit() == False:
                        last_hour_idx = idx
                        break

                stop['schedule'] = stop['schedule'][0][1:last_hour_idx]

            for stop in line['direction2']['stops']:
                stop['name'] = stop['name'].strip()

                last_hour_idx = None
                for idx, times in enumerate(stop['schedule'][0][1:]):
                    if times[0].isdigit() == False:
                        last_hour_idx = idx
                        break
                    
                stop['schedule'] = stop['schedule'][0][1:last_hour_idx]

        return main_schedule['lines']
