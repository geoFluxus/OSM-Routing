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
* osmpgrouting.py: The main Python script for using the app

## User's Documentation
Given that Python 3 is already installed, start the application using osm
It is also possible to further extend an available database; new additions are snapped (if necessary) to the existent road network and the general topology is updated to incorporate the changes.

