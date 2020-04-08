from geom import (pp_distance,
                  ps_distance,
                  explode,
                  bbox,
                  bbox_intersects,
                  projection)
from simplify import Simplify

class Snapper():
    def __init__(self, segments, reference,
                 threshold=0.01):
        self.segments = segments  # to be snapped
        self.reference = reference  # reference geometry
        self.vertices = set() # reference vertices
        self.threshold = threshold  # snap threshold
        self.snapped = []  # snapped segments

    # recover reference points
    def reference_points(self, seg):
        vertices = set()
        seg_bbox = bbox(seg, self.threshold)
        for ref in self.reference:
            if bbox_intersects(ref, seg_bbox):
                for point in ref:
                    vertices.add(point)
        return vertices

    # FIRST SNAPPING STAGE
    # snap edges to points
    def point_snap(self):
        self.snapped = []

        # iterate segments
        for segment in self.segments:
            pts = [] # points to form the snapped segment
            self.vertices = self.reference_points(segment)
            for pt in segment:
                # check reference points
                # for nearest point
                min, nearest = float('Inf'), None
                for vex in self.vertices:
                    dist = pp_distance(pt, vex)
                    if dist < min and dist <= self.threshold**2:
                        min = dist
                        nearest = vex

                # if not such point found
                # use original point
                if nearest:
                    pts.append(nearest)
                else:
                    pts.append(pt)

            # append new segment
            # if it is valid
            if len(pts) >= 2:
                # remove invalid segments of zero length
                valid = []
                for pt in pts:
                    if pt not in valid: valid.append(pt)
                self.snapped.append(valid)

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

    # snap line layer to line layer
    def snap(self):
        self.point_snap()  # point snap
        self.edge_snap()  # edge snap

        # stringify snapped layer
        segments = []
        for seg in self.segments:
            for i in range(len(seg)-1):
                segment = (seg[i], seg[i+1])
                # remove duplicates
                if segment not in segments:
                    segments.append(segment)
        simplify = Simplify()
        simplify.segments = segments
        simplify.stringify(False)
        self.segments = simplify.segments








