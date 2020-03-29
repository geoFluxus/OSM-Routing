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





