from osmparser import OSMparser

parser = OSMparser()
parser.readfile()

ways = parser.ways
nodes = parser.nodes

# Write node file
filename = '/home/geofluxus/Desktop/ways.csv'
fil = open(filename, 'w')
fil.write('id;wkt\n')
for id, refs in ways.items():
    geom = 'LINESTRING('
    for ref in refs:
        lon, lat = nodes[ref]
        geom += '{} {},'.format(lat, lon)
    geom = geom[:-1] + ')'
    line = '{};{}\n'.format(id, geom)
    fil.write(line)
fil.close()