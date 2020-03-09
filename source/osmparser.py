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

# Open file
try:
    fil = open(filename, 'r')
except FileNotFoundError:
    raise FileNotFoundError('File not found...')


# Skip the first lines
for i in range(3):
    line = fil.readline()


# Read file
nodes = {}
ways = {}

print('Parsing file...')
while line:
    line = fil.readline()

    # process nodes
    if '<node' in line:
        # recover tags
        tags = line.replace('<node ', '') \
            .replace('>', '') \
            .replace('/', '') \
            .split()

        # id / lat /lon
        id = tags[0].strip('id=').strip('"')
        lat = float(tags[1].strip('lat=').strip('"'))
        lon = float(tags[2].strip('lon=').strip('"'))
        nodes[id] = (lat, lon)

    # process ways
    if '<way' in line:
        # read id
        id = line.replace('<way id="', '')\
                 .replace('">', '')\
                 .strip('\t')\
                 .strip('\n')
        # initialize way
        ways[id] = []
        # recover all node refs
        while '</way>' not in line:
            # read node ref
            line = fil.readline()
            if '<nd' not in line: break
            ref = line.replace('<nd ref="', '')\
                      .replace('"/>', '')\
                      .strip('\t')\
                      .strip('\n')
            # append to way
            ways[id].append(ref)
print('Parsing complete...')

# CLOSE file
fil.close()

# # Write node file
# filename = desktop + '/ways.csv'
# fil = open(filename, 'w')
# fil.write('id;wkt\n')
# for id, refs in ways.items():
#     geom = 'LINESTRING('
#     for ref in refs:
#         lon, lat = nodes[ref]
#         geom += '{} {},'.format(lat, lon)
#     geom = geom[:-1] + ')'
#     line = '{};{}\n'.format(id, geom)
#     fil.write(line)
# fil.close()