.PHONY: simulation simulation_first equirements simulation scrape osm data all

requirements:
	pip install -r requirements.txt

scrape:
	python webscrape/main.py

osm:
	python openstreetmap/main.py

data:
	python datapreprocessing/main.py

simulation:
	python simulation/main.py

simulation_first:
	python simulation/main.py --first-run

all:
	make scrape osm data simulation 

