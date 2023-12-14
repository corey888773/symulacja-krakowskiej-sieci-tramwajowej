requirements:
	pip install -r requirements.txt

scrape:
	python webscrape/main.py

osm:
	python openstreetmap/main.py

data:
	python datapreprocessing/main.py

.PHONY: simulation
simulation:
	python simulation/main.py

.PHONY: simulation_first
simulation_first:
	python simulation/main.py --first-run

all:
	make scrape osm data simulation 

.PHONY:
	requirements simulation scrape osm data all