from simulation import Simulation
import json


def main() -> None:
    with open("../datapreprocessing/data/physical_network.json", "r", encoding="utf8") as f:
        network_model_physical = json.load(f)

    with open("../datapreprocessing/data/logical_network.json", "r", encoding="utf8") as f:
        network_model_logical = json.load(f)

    simulation = Simulation(network_model_logical, network_model_physical)
    simulation.run()


if __name__ == '__main__':
    main()
    