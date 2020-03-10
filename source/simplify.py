from osmparser import OSMparser

# read osm file
parser = OSMparser()
parser.readfile()

# recover parameters
path = parser.path
nodes = parser.nodes
ways = parser.ways

print('Initialize simplification...')

print('[STEP 1]')
print('Build network graph...')
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
        processed[segment] = False  # mark edge as not processed
        for vex in segment:
            if vex not in graph.keys():
                graph[vex] = [segment]
            else:
                graph[vex].append(segment)

print('Network graph complete...\n')
print('[STEP 2]')
print('Identify intersections...')


# check if graph vertex is intersection
def is_intersection(vex, edges):
    # TEST 1
    # check if vertex is an orphan point
    # (part of only one edge)
    if len(edges) == 1:
        # start / end point of edge
        geom = edges[0]
        start, end = geom[0], geom[-1]

        # check if vertex is equal to
        # start or end point
        if (vex == start) or \
           (vex == end):
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

print('Intersections recorded...\n')
print('[STEP 3]')
print('Stringify...')


# traverse intersections
segments = set()
for inter, is_inter in inters.items():
    # not intersection, skip
    if not is_inter: continue

    # traverse all edges of the intersection!
    edges = graph[inter]
    for edge in edges:
        # edge processed, skip
        if processed[edge]: continue

        # start search
        STOP = False

        # start point sequence with intersection
        pts = [inter]

        # jump from edge to edge
        # till reaching another intersection
        curr_pos = inter
        curr_edge = edge
        while not STOP:
            # get edge geometry
            geom = curr_edge

            # check start point edge
            # if different from intersection, reverse edge
            # current intersection should be the starting point!
            start = geom[0]
            if start != curr_pos:
                geom = geom[::-1]
                start = geom[0]
                if start != curr_pos:
                    break

            # traverse edge
            for pt in geom[1:]:  # the intersection has been added!
                # collect point
                pts.append(pt)

                # if intersection == STOP!
                curr_pos = pt
                if inters[curr_pos]:
                    STOP = True
                    break

            # mark edge as processed
            processed[curr_edge] = True

            # jump to next edge
            # with end point of current edge
            adjacent = graph[curr_pos]
            for adj in adjacent:
                if not(processed[adj]):
                    curr_edge = adj
                    break

        segments.add(tuple(pts))

# write intersection file
filename = path + '/segments.csv'
fil = open(filename, 'w')
fil.write('wkt\n')
for segment in segments:
    line = 'LINESTRING('
    for point in segment:
        lat, lon = point
        line += '{} {},'.format(lon, lat)
    line = line[:-1] + ')\n'
    fil.write(line)
fil.close()