from tkinter import filedialog
from tkinter import *
import os

# Check OS
if os.name == 'nt':
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
elif os.name == 'posix':
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
else:
    raise ValueError('OS not supported...')

# Menu to open file
root = Tk()
root.filename = filedialog.askopenfilename(initialdir=desktop,
                                           title="Select file",
                                           filetypes=(("OSM","*.osm"),
                                                      ("all files","*.*")))

# File to be processed
filename = root.filename

# Open :file
try:
    fil = open(filename, 'r')
except FileNotFoundError:
    raise FileNotFoundError('File not found...')


# Skip the first lines
for i in range(3):
    line = fil.readline()

# Read node
def read_node(line):
    tags = line.replace('<node ', '') \
               .replace('>', '') \
               .replace('/', '') \
               .split()

    # id / lat /lon
    id = tags[0].strip('id=').strip('"')
    lat = float(tags[1].strip('lat=').strip('"'))
    lon = float(tags[2].strip('lon=').strip('"'))
    nodes[id] = (lat, lon)

# Read file
nodes = {}
while line:
    line = fil.readline()

    # process nodes
    if '<node' in line:
        read_node(line)

# CLOSE file
fil.close()

# # Write node file
# filename = desktop + '/nodes.csv'
# fil = open(filename, 'w')
# fil.write('id;wkt\n')
# for id, coords in nodes.items():
#     lat, lon = coords
#     line = '{};POINT({} {})\n'.format(id, lon, lat)
#     fil.write(line)
# fil.close()