import json, logging

from networks import process_physical_network

# logger configuration
logging.basicConfig(format='%(levelname)s - %(filename)s:%(lineno)d, message: %(message)s', level=logging.DEBUG)

def main():

    with open('../openstreetmap/open-street-map.json', 'r') as f:
        trams_osm = json.load(f)
    with open('../webscrape/schedule.json', 'r') as f:
        trams_schedule = json.load(f)

    # physcial_network = process_physical_network(trams_osm)

if __name__ == "__main__":
    main()

