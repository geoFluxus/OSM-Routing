class Snapper():
    def __init__(self, segments, reference,
                 threshold=0.01):
        self.segments = segments  # to be snapped
        self.reference = reference  # reference geometry
        self.vertices = self.reference_points()
        self.threshold = threshold

    # recover reference points
    def reference_points(self):
        vertices = set()
        for segment in self.reference:
            for point in segment:
                vertices.add(point)
        return vertices

    # point-point distance
    @staticmethod
    def pp_distance(p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return dx**2 + dy**2

    # FIRST SNAPPING STAGE
    # snap edges to points
    def point_snap(self):
        segments = []

        # iterate segments
        for segment in self.segments:
            pts = [] # points to form the snapped segment
            for pt in segment:
                # check reference points
                found = False
                for vex in self.vertices:
                    # if reference point within snapping distance
                    # interchange original point with that
                    if self.pp_distance(pt, vex) <= self.threshold**2:
                        # avoid snapping two original points
                        # at the same reference point
                        if vex not in pts:
                            pts.append(vex)
                        found = True
                        break

                # if not such point found
                # use original point
                if not found: pts.append(pt)

            # append new segment
            # if it is valid (at least two not identical points)
            if len(pts) >= 2:
                segments.append(pts)

        # when done, replace
        self.segments = segments

    # explode linestring geometry
    @staticmethod
    def explode(geometry):
        exploded = []
        for line in geometry:
            n = len(line) - 1
            for i in range(n):
                segment = [line[i], line[i+1]]
                exploded.append(segment)
        return exploded

    # side test for point-segment
    def side(self, p, seg):
        p1, p2 = seg
        t1 = (p[0] - p1[0]) * (p2[1] - p1[1])
        t2 = (p2[0] - p1[0]) * (p[1] - p1[1])
        side = t1 - t2
        if side < 0:
            return -1
        elif side > 0:
            return 1
        return 0

    # intersect test for segments
    def intersect(self, s_a, s_b):
        side_a = self.side(s_a[0], s_b)
        side_b = self.side(s_a[1], s_b)
        side_c = self.side(s_b[0], s_a)
        side_d = self.side(s_b[1], s_a)
        if (side_a != side_b) and \
                (side_c != side_d):
            return True
        return False

    # point-segment distance
    @staticmethod
    def ps_distance(pt, seg):
        # define coordinates
        p1, p2 = seg
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = pt

        # compute distance vector
        px = x2 - x1
        py = y2 - y1

        # compute norm
        norm = px * px + py * py
        # if norm equals zero
        # the point lies on the segment (ignore)
        if norm == 0: return -1

        # compute parameter
        u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)

        # point lies "outside" of segment
        # also ignore
        if u > 1 or u < 0:
            return -1

        # line parametric equations
        # to compute point projection on segment
        x = x1 + u * px
        y = y1 + u * py

        # compute distance vector
        # between point and projection
        dx = x - x3
        dy = y - y3

        return dx * dx + dy * dy

    # SECOND SNAPPING STAGE
    # snap edges tp edges
    def edge_snap(self):
        # explode to simple segments
        self.reference = self.explode(self.reference)
        self.segments = self.explode(self.segments)








