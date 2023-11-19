import json, logging, os

from networks import process_physical_network, process_logical_network

# logger configuration
logging.basicConfig(format='%(levelname)s - %(filename)s:%(lineno)d, message: %(message)s', level=logging.DEBUG)
curr_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    with open(f'{curr_dir}/../openstreetmap/open-street-map.json', 'r') as f:
        trams_osm = json.load(f)
    with open(f'{curr_dir}/../webscrape/schedule.json', 'r') as f:
        trams_schedule = json.load(f)

    physcial_network = process_physical_network(trams_osm)
    logical_network = process_logical_network(trams_schedule, physcial_network)

    with open(f'{curr_dir}/data/physical_network.json', 'w') as f:
        json.dump(physcial_network.to_json(), f, indent=2, ensure_ascii=False)
    with open(f'{curr_dir}/data/logical_network.json', 'w') as f:
        json.dump(logical_network.to_json(), f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()

