from simulation import Simulation
import json
import os
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-run", action="store_true")
    args = parser.parse_args()

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{curr_dir}/../datapreprocessing/data/physical_network.json", "r", encoding="utf8") as f:
        network_model_physical = json.load(f)

    with open(f"{curr_dir}/../datapreprocessing/data/logical_network.json", "r", encoding="utf8") as f:
        network_model_logical = json.load(f)

    simulation = Simulation(network_model_logical, network_model_physical, is_first_run=args.first_run)
    simulation.run()


if __name__ == '__main__':
    main()
    