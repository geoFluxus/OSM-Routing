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
        row = 'POINT({} {})\n'.format(lon, lat)
        fil.write(row)
    fil.close()

# export line layer (.csv)
def export_lines(lines, name):
    filename = path + '/' + name + '.csv'
    fil = open(filename, 'w')
    fil.write('wkt\n')
    for line in lines:
        row = 'LINESTRING('
        for point in line:
            lat, lon = point
            row += '{} {},'.format(lon, lat)
        row = row[:-1] + ')\n'
        fil.write(row)
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
simplify.record_intersections()
intersections = simplify.intersections
print('Intersections recorded...\n')

# stringify
print('[STEP 3]')
print('Stringify...')
simplify.stringify()
segments = simplify.segments
export_lines(segments, 'stringify')
print('Stringify complete...\n')


