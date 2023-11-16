import json, logging, os

from networks import process_physical_network, process_logical_network
from schedule_utils import prettify_schedule

# logger configuration
logging.basicConfig(format='%(levelname)s - %(filename)s:%(lineno)d, message: %(message)s', level=logging.DEBUG)

def main():
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f'{curr_dir}/../openstreetmap/open-street-map.json', 'r') as f:
        trams_osm = json.load(f)
    with open(f'{curr_dir}/../webscrape/schedule.json', 'r') as f:
        trams_schedule = json.load(f)

    physcial_network = process_physical_network(trams_osm)
    trams_schedule = prettify_schedule(trams_schedule)
    logical_network = process_logical_network(trams_schedule, physcial_network)


if __name__ == "__main__":
    main()

