from osmparser import OSMparser

# read osm file
parser = OSMparser()
parser.readfile()

# recover parameters
path = parser.path
nodes = parser.nodes
ways = parser.ways


# create graph
# { vertex : adjacent_edges }
graph = {}

# keep track of processed edges
processed = {}

# traverse all linestrings
for points in ways.values():
    # split into segments
    n = len(points) - 1
    segments = []
    for i in range(n):
        start, end = nodes[points[i]], nodes[points[i+1]]
        segment = (start, end)
        segments.append(segment)

    # process segments
    for segment in segments:
        processed[segment] = False # mark edge as not processed
        for vex in segment:
            if vex not in graph.keys():
                graph[vex] = [segment]
            else:
                graph[vex].append(segment)


# check if graph vertex is intersection
def is_intersection(vex, edges):
    # TEST 1
    # check if vertex is an orphan point
    # (part of only one edge)
    if len(edges) == 1:
        # start / end point of edge
        geom = edges[0]
        start, end = geom[0], geom[1]

        # check if vertex is equal to
        # start or end point
        x, y = vex[0], vex[1]
        if (x == start[0] and y == start[1]) or \
           (x == end[0] and y == end[1]):
            return True

    # TEST 2
    # More than two adjacent edges == intersection !
    if len(edges) > 2:
        return True

    return False

# record intersections
inters = {}
for vex, edges in graph.items():
    if is_intersection(vex, edges):
        # mark as intersection
        inters[vex] = True
    else:
        inters[vex] = False

# write node file
filename = path + '/ways.csv'
fil = open(filename, 'w')
fil.write('wkt\n')
for inter, is_inter in inters.items():
    if is_inter:
        lat, lon = inter
        line = 'POINT({} {})\n'.format(lon, lat)
        fil.write(line)
fil.close()