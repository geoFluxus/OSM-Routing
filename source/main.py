from osmparser import OSMparser
from simplify import Simplify
import tkinter as tk
from tkinter import messagebox

# export point layer (.csv)
def export_points(points, name):
    filename = path + '/' + name + '.csv'
    fil = open(filename, 'w')
    fil.write('wkt\n')
    for point in points:
        lat, lon = point
        line = 'POINT({} {})\n'.format(lon, lat)
        fil.write(line)
    fil.close()

# read osm file
parser = OSMparser()
parser.readfile()

# recover parameters
path = parser.path

# recover network
network = {}
network['ways'] = parser.ways
network['nodes'] = parser.nodes

# initialize simplification
print('[PROCESS] Simplification')
simplify = Simplify(network)

# recover initial topology
print('[STEP 1]')
print('Build network graph...')
simplify.build_graph()
print('Network graph complete...\n')

# record intersections
print('[STEP 2]')
print('Identify intersections...')
intersections = simplify.record_intersections()
print('Intersections recorded...\n')

points = []
for point, is_intersection in intersections.items():
    if is_intersection: points.append(point)
export_points(points, 'intersections')
# print('[STEP 3]')
# print('Stringify...')