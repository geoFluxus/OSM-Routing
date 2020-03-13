class Simplify():
    def __init__(self, network={}, resolution=0.01):
        self.ways = network['ways']
        self.nodes = network['nodes']
        self.graph = {} # network graph
        self.processed = {} # processed edge inventory
        self.intersections = {} # intersection inventory
        self.segments = [] # segment storage
        self.clustered = {} # clustered intersection inventory
        self.clusters = [] # intersection clusters
        self.resolution = resolution

    # recover original topology
    def build_init_graph(self):
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
    @staticmethod
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
    def record_intersections(self):
        # clear intersections
        self.intersections = {}

        # traverse graph
        for vex, edges in self.graph.items():
            if self.is_intersection(vex, edges):
                # mark as intersection
                self.intersections[vex] = True
            else:
                self.intersections[vex] = False

    # stringify network
    def stringify(self, init=True):
        if init:
            # build initial graph
            self.build_init_graph()
        else:
            # build new graph
            self.build_new_graph()

        # clear stored segments
        self.segments = []

        # record intersections
        self.record_intersections()

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

    # recover topology of stringified network
    def build_new_graph(self):
        # build new graph
        self.graph = {}

        # traverse network segments
        self.processed = {}
        for segment in self.segments:
            # mark as not processed
            self.processed[tuple(segment)] = False

            # each string has as edge points
            # ALWAYS intersections
            for vex in [segment[0], segment[-1]]:
                if vex in self.graph.keys():
                    self.graph[vex].append(segment)
                else:
                    self.graph[vex] = [segment]
                    self.clustered[vex] = False

    # compute point distance
    @staticmethod
    def compute_dist(o, d):
        dx = d[0] - o[0]
        dy = d[1] - o[1]
        return dx**2 + dy**2

    # distance clustering
    def cluster(self):
        # build new graph
        self.build_new_graph()

        # iterate intersections
        inters = list(self.graph.keys())
        num = len(inters)
        for i in range(num):
            orig = inters[i]
            if self.clustered[orig]: continue

            # form cluster by distance
            cluster = []
            for j in range(i, num):
                dest = inters[j]
                if self.clustered[dest]: continue

                dist = self.compute_dist(orig, dest)
                if dist <= self.resolution ** 2:
                    cluster.append(dest)
                    self.clustered[dest] = True

            self.clusters.append(cluster)

    # compute cluster centroid
    @staticmethod
    def compute_centroid(cluster):
        if len(cluster) >= 2:
            n = len(cluster)
            x = sum([pt[0] for pt in cluster])
            y = sum([pt[1] for pt in cluster])
            return x / n, y / n
        else:
            return cluster[0]

    # simplify network with intersection clustering
    def simplify(self):
        # clustering
        self.cluster()

        # process groups
        centroid_graph = {}
        for cluster in self.clusters:
            # compute centroid
            centroid = self.compute_centroid(cluster)

            # collect all related edges
            edges = set()
            for inter in cluster:
                inter_edges = self.graph[inter]
                inter_edges = [tuple(edge) for edge in inter_edges]
                edges.update(inter_edges)

            # add to graph
            centroid_graph[centroid] = edges

        # form new segments
        self.segments = []
        centroids = list(centroid_graph.keys())
        num = len(centroids)
        for i in range(num):
            curr_centroid = centroids[i]
            curr_edges = centroid_graph[curr_centroid]

            for j in range(i+1, num):
                other_centroid = centroids[j]
                edges = centroid_graph[other_centroid]
                common = edges.intersection(curr_edges)
                if len(common) > 0:
                    segment = (curr_centroid, other_centroid)
                    self.segments.append(segment)

        # stringify once more
        self.stringify(False)
