# OSM-Routing (latest version: v0.1)
OSM Data Processing for the construction of lightweight routable networks (compatible with pgRouting)

## Dependencies
Currently, the application is implemented in Python 3. For enabling the database storing functionalities, the following dependencies are also necessary:
* [psycopg2](https://pypi.org/project/psycopg2/): Enables database connection
* [PostgreSQL](https://www.postgresql.org/): The latest version has been tested with PostgreSQL v10
* [PostGIS](https://postgis.net/): The latest version has been tested on PostGIS v2.5. Along with PostgreSQL, enables the creation, management and processing of geodatabases
* [pgRouting](https://pgrouting.org/): The latest version has been tested with pgRouting v3

## Introduction
With this application, you can convert OSM road network data into lightweight routable networks. You can extract the simplification results as .csv files (compatible with any GIS environment) or store them directly into a pgRouting-compatible database.

<p align="center">
  <b>Figure 1. Road network simplification</b>
</p>

| <img src="https://github.com//VasileiosBouzas/OSM-Routing/raw/master/img/original.png" alt="Original" width="400" hspace="20"> | <img src="https://github.com//VasileiosBouzas/OSM-Routing/raw/master/img/simplified.png" alt="Simplified" width="400"> |
|:---:|:---:|
| **Original (23132 segments)** | **Simplified (1291 segments)** |

