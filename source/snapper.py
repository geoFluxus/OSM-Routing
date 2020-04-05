from source.geom import (pp_distance,
                         ps_distance,
                         explode,
                         bbox,
                         bbox_contains,
                         bbox_intersects,
                         intersects,
                         projection)

class Snapper():
    def __init__(self, segments, reference,
                 threshold=0.01):
        self.segments = segments  # to be snapped
        self.reference = reference  # reference geometry
        self.vertices = self.reference_points()
        self.threshold = threshold
        self.snapped = []  # snapped segments

    # recover reference points
    def reference_points(self):
        vertices = set()
        for segment in self.reference:
            for point in segment:
                vertices.add(point)
        return vertices

    # FIRST SNAPPING STAGE
    # snap edges to points
    def point_snap(self):
        self.snapped = []

        # iterate segments
        for segment in self.segments:
            pts = [] # points to form the snapped segment
            for pt in segment:
                # check reference points
                found = False
                for vex in self.vertices:
                    # if reference point within snapping distance
                    # interchange original point with that
                    if pp_distance(pt, vex) <= self.threshold**2:
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
                self.snapped.append(pts)

        # when done, replace
        self.segments = self.snapped

    # SECOND SNAPPING STAGE
    # snap edges to edges
    def edge_snap(self):
        # explode to simple segments
        self.reference = explode(self.reference)
        self.segments = explode(self.segments)

        # iterate exploded segments
        self.snapped = []
        for seg in self.segments:
            # if segment exists in reference,
            # ignore it (regardless of orientation)
            if seg in self.reference or \
               seg[::-1] in self.reference:
                continue

            # search for reference segments
            # intersecting segment bbox
            # enlarged by snapping threshold
            refs = []
            seg_bbox = bbox(seg, self.threshold)  # enlarged bbox
            for ref in self.reference:
                # bbox intersection
                if bbox_intersects(ref, seg_bbox):
                    refs.append(ref)

            # if no refs, append segment
            if not refs:
                self.snapped.append(seg)
            else:
                # check for ref points
                # to project on current segment
                pts = set()  # unique points
                # iterate intersecting ref segments
                for ref in refs:
                    for pt in ref:
                        # check if point is within snap threshold
                        # do not bother with zero distance points
                        # they are already projected!
                        dist = ps_distance(pt, seg)
                        if dist <= self.threshold**2 and \
                           dist != 0:
                            pts.add(pt)

                # if no projections, append segment
                if not pts:
                    self.snapped.append(seg)
                else:
                    projs = []
                    for pt in pts:
                        projs.append(projection(pt, seg))
                    seg.extend(projs)
                    seg.sort(key=lambda pt: pt[0])
                    self.snapped.append(seg)

        # replace
        self.segments = self.snapped
        self.point_snap()








