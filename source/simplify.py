class Simplify():
    def __init__(self, network):
        self.ways = network['ways']
        self.nodes = network['nodes']
        self.graph = {} # network graph
        self.processed = {} # keep track of processed edges
        self.intersections = {} # intersection inventory
        self.segments = [] # segment storage

    # recover original topology
    def build_graph(self):
        # traverse all linestrings
        for points in self.ways.values():
            # split into segments
            n = len(points) - 1
            self.segments = []
            for i in range(n):
                start, end = self.nodes[points[i]], self.nodes[points[i + 1]]
                segment = (start, end)
                self.segments.append(segment)

            # process segments
            for segment in self.segments:
                self.processed[segment] = False  # mark edge as not processed
                for vex in segment:
                    if vex not in self.graph.keys():
                        self.graph[vex] = [segment]
                    else:
                        self.graph[vex].append(segment)

    # check if graph vertex is intersection
    def is_intersection(self, vex, edges):
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
    def record_intersections(self):
        for vex, edges in self.graph.items():
            if self.is_intersection(vex, edges):
                # mark as intersection
                self.intersections[vex] = True
            else:
                self.intersections[vex] = False

    # stringify network
    def stringify(self):
        # clear stored segments
        self.segments = []

        # traverse intersection inventory
        for inter, is_inter in self.intersections.items():
            # not intersection, skip
            if not is_inter: continue

            # traverse all edges of the intersection!
            edges = self.graph[inter]
            for edge in edges:
                # edge processed, skip
                if self.processed[edge]: continue

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
                        if self.intersections[curr_pos]:
                            STOP = True
                            break

                    # mark edge as processed
                    self.processed[curr_edge] = True

                    # jump to next edge
                    # with end point of current edge
                    adjacent = self.graph[curr_pos]
                    for adj in adjacent:
                        if not(self.processed[adj]):
                            curr_edge = adj
                            break

                self.segments.append(pts)
#
#
# # Stringify menu
# def export_stringify():
#     filename = path + '/stringify.csv'
#     fil = open(filename, 'w')
#     fil.write('wkt\n')
#     for string in stringify:
#         line = 'LINESTRING('
#         for point in string:
#             lat, lon = point
#             line += '{} {},'.format(lon, lat)
#         line = line[:-1] + ')\n'
#         fil.write(line)
#     fil.close()
#
# root = tk.Tk()
# root.withdraw()
# # Check to export stringify
# msgbox = tk.messagebox.askquestion('Export file',
#                                    'Want to export stringified network?',
#                                    icon='warning')
# if msgbox == 'yes':
#     tk.messagebox.showinfo('Message',
#                            'File exported in desktop...')
#     export_stringify()
# # Check to continue processing
# msgbox = tk.messagebox.askquestion('WARNING!',
#                                    'Continue processing?',
#                                    icon='warning')
# if msgbox == 'no':
#     root.destroy()
#     exit()
#
#
# print('[STEP 4]')
# print('Build new graph')
# # build new graph
# graph = {}
# grouped = {} # mark as grouped
# for string in stringify:
#     # each string has as edge points
#     # ALWAYS intersections
#     for vex in [string[0], string[-1]]:
#         if vex in graph.keys():
#             graph[vex].append(string)
#         else:
#             graph[vex] = [string]
#             grouped[vex] = False
# print('New graph complete...\n')
#
#
# print('[STEP 5]')
# print('Cluster intersections...')
# def compute_dist(o, d):
#     dx = d[0] - o[0]
#     dy = d[1] - o[1]
#     return dx**2 + dy**2
#
# # iterate intersections
# inters = list(graph.keys())
# num = len(inters)
# groups, gnum = [], 0
# thres = 0.01
# for i in range(num):
#     orig = inters[i]
#     if grouped[orig]: continue
#
#     # form group by distance
#     group = []
#     for j in range(i, num):
#         dest = inters[j]
#         if grouped[dest]: continue
#
#         dist = compute_dist(orig, dest)
#         if dist <= thres ** 2:
#             group.append(dest)
#             grouped[dest] = True
#
#     groups.append(group)
#     gnum += 1
# print('Clustering complete...\n')
#
#
# print('[STEP 6]')
# print('Rebuild network...')
# def compute_centroid(group):
#     if len(group) >= 2:
#         n = len(group)
#         x = sum([pt[0] for pt in group])
#         y = sum([pt[1] for pt in group])
#         return x / n, y / n
#     else:
#         return group[0]
#
# # process groups
# centroid_graph = {}
# for group in groups:
#     # compute centroid
#     centroid = compute_centroid(group)
#
#     # collect all related edges
#     edges = set()
#     for inter in group:
#         inter_edges = graph[inter]
#         inter_edges = [tuple(edge) for edge in inter_edges]
#         edges.update(inter_edges)
#
#     # add to graph
#     centroid_graph[centroid] = edges
#
# # form centroid connections
# connections = {}
# centroids = list(centroid_graph.keys())
# num = len(centroids)
# for i in range(num):
#     curr_centroid = centroids[i]
#     curr_edges = centroid_graph[curr_centroid]
#     connections[curr_centroid] = []
#
#     for j in range(i+1, num):
#         other_centroid = centroids[j]
#         edges = centroid_graph[other_centroid]
#         common = edges.intersection(curr_edges)
#         if len(common) > 0:
#             connections[curr_centroid].append(other_centroid)
#
# stringify = []
# for orig, dests in connections.items():
#     for dest in dests:
#         # define geometry
#         string = [orig, dest]
#         stringify.append(string)
#
# export_stringify()
# print('Network complete...\n')