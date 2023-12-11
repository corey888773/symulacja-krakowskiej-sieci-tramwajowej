from simulation import Simulation
import json
import os


def main() -> None:
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{curr_dir}/../datapreprocessing/data/physical_network.json", "r", encoding="utf8") as f:
        network_model_physical = json.load(f)

    with open(f"{curr_dir}/../datapreprocessing/data/logical_network.json", "r", encoding="utf8") as f:
        network_model_logical = json.load(f)

    simulation = Simulation(network_model_logical, network_model_physical, is_first_run=False)
    simulation.run()


if __name__ == '__main__':
    main()
    