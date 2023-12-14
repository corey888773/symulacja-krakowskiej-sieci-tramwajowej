# TRAM NETWORK SIMULATION IN CRACOW
The application is written in Python language, using Pygame library for visualization. 
The simulation allows you to track the movement of trams in Cracow based on previously prepared data in JSON format. 
Detailed information on how the program works is presented below.


## Built With
- Python
- pygame
- numpy
- matplotlib
- beautifulsoup
- html-table-parser
- requests
- shapely
- urllib3



## Getting Started
1. Clone the repo
   ```sh
   git clone https://github.com/corey888773/symulacja-krakowskiej-sieci-tramwajowej.git
   ```
2. To start the project, you need to have Python and Miniconda installed on your computer.

    [Download python](https://www.python.org/downloads/)

    [Download miniconda](https://javedhassans.medium.com/install-miniconda-on-linux-from-the-command-line-in-5-steps-403912b3f378)

3. Set on the project directory.
4. Set up the virtual environment:
   ```sh
   conda create -n <env_name> python=3.12 pip
   conda activate <env_name>
   conda install --file requirements.txt
   ```  
5. Set up the project data:
   ```sh
   make all
   ```
6. Run the project:
   ```sh
   make simulation
   ```
   
## Data preprocessing
Example JSON:
```json
[
  {
    "model": "BMW",
    "price": 120,
    "color": "BLACK",
    "mileage": 1500,
    "components": [
      "ABS",
      "ALLOY WHEELS"
    ]
  },
  {
    "model": "MAZDA",
    "price": 160,
    "color": "WHITE",
    "mileage": 2500,
    "components": [
      "AIR CONDITIONING",
      "BLUETOOTH"
    ]
  }
]
```


```python
def main() -> None:
   FILENAME: Final[str] = 'cars_app/data/cars.json'
   cars_data = get_cars_data(FILENAME)
   cars = get_cars(cars_data)
   cars_service = CarsService(cars)

   print(cars_service.get_cars_with_mileage_greater_than(1500))
   print(cars_service.get_color_and_no_of_cars())
   print(cars_service.get_model_and_most_expensive_car())

```


## Simulation and visualization
Example JSON:
```json
{
    "5": [
        "Tram(id=0, current_stop=TramStop(id=2420153432, x=309.79131857276855, y=348.877981038998, stop_name=StaryKleparz01), passengers=17, route_id=5)",
        "Tram(id=1, current_stop=TramStop(id=2163355810, x=831.9876346931595, y=277.8015801670025, stop_name=Struga02), passengers=74)"
    ],
    "35": [
        "Tram(id=0, current_stop=TramStop(id=288916414, x=415.1175022393605, y=550.8455212750316, stop_name=PodgórzeSKA02) passengers=66)"
    ]
}
```


```python
print('hello')
```

## Contributing
If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/new-feature`)
3. Commit your Changes (`git commit -m 'Add some new-feature'`)
4. Push to the Branch (`git push origin feature/new-feature`)
5. Open a Pull Request


## License
Distributed under the MIT License. See `LICENSE.txt` for more information.


## Contact
Szymon Frączek - szymoon09@gmail.com

Piotr Gąsiorek - kdzielnicka@gmail.com

Kaja Dzielnicka - pgasiorek773@gmail.com
