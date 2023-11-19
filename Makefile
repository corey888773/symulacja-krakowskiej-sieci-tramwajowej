requirements:
	pip install -r requirements.txt

scrape:
	python webscrape/main.py

osm:
	python openstreetmap/main.py

data:
	python datapreprocessing/main.py

all:
	make scrape osm data

.PHONY:
	requirements scrape osm data