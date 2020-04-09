# OSM-Routing (latest version: v0.1)
OSM Data Processing for the construction of lightweight routable networks (compatible with pgRouting)

## Dependencies
Currently, the application is implemented in Python 3. For enabling the database storing functionalities, the following dependencies are also necessary:
* [psycopg2](https://pypi.org/project/psycopg2/): Enables database connection
* [PostgreSQL](https://www.postgresql.org/): The latest version has been tested with PostgreSQL v10
* [PostGIS](https://postgis.net/): The latest version has been tested on PostGIS v2.5. Along with PostgreSQL, enables the creation, management and processing of geodatabases
* [pgRouting](https://pgrouting.org/): The latest version has been tested with pgRouting v3

## Introduction
With this application, you can convert OSM road network data into lightweight routable networks. You can either extract the simplification results as .csv files (compatible with any GIS environment) or store them directly into a pgRouting-compatible database (read more in **Dependencies**).

<p align="center">
  <b>Figure 1. Road network simplification</b>
</p>

| <img src="https://github.com//VasileiosBouzas/OSM-Routing/raw/master/img/original.png" alt="Original" width="400" hspace="20"> | <img src="https://github.com//VasileiosBouzas/OSM-Routing/raw/master/img/simplified.png" alt="Simplified" width="400"> |
|:---:|:---:|
| **Original (23132 segments)** | **Simplified (1291 segments)** |

## Content
The Github repo contains the following:
* /data: Includes several .osm files to test the app
* /source: Contains all the source code fot the app
* osmrouting.py: The main Python script for using the app

## User's Documentation
### Getting started
Given that Python 3 is already installed, start the application by firing osmrouting.py. There are several options for that:
* Use your preferred Python IDE
* Open terminal in the OSM-Routing dierctory and use the command: python3 osmpgrouting.py

### Defining input
At first, you need to select the .osm file containing the network data (**Pay attention!!!** Currently, only pre-filtered .osm files containing network data are supported. It is still possible to use .osm files either accessed in online platforms (i.e. [GEOFABRIK](http://download.geofabrik.de/)) or downloaded through other means. To pre-process them , use [osmconvert](http://download.geofabrik.de/) to interchange between various OSM file formats and [osmfilter](https://wiki.openstreetmap.org/wiki/Osmfilter) to filter out only road-related data).

### Simplification
After the .osm file is parsed, specify the simplification resolution. This resolution should be provided **[in decimal degrees](https://en.wikipedia.org/wiki/Decimal_degrees)** (if you skip that step, the default value of **0.01** degrees will be used). After the simplification is complete, the result is exported to **desktop** in .csv format. To open it, use any open-source or commercial GIS platform - for example, you can import this file format as a layer in [QGIS](https://qgis.org/en/site/) through Layer > Add Layer > Add Delimited Text Layer.

# Storing to database (optional)
Once the simplification is finished, you will be requested to store to a prRouting-compatible geodatabase. **Before that**, make sure that you create a PostgreSQL database with **PostGIS** and **pgRouting** extensions. It is also possible to further extend an available database; new additions are snapped (if necessary) to the existent road network and the general topology is updated to incorporate the changes.

