from source.geom import (pp_distance,
                         ps_distance,
                         explode,
                         bbox,
                         bbox_contains,
                         bbox_intersects,
                         intersects)

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

    # edge snap
    def snap(self, seg, ref):
        def nearest_point(pt, ref):
            min, min_pt = float('Inf'), None
            for p in ref:
                dist = pp_distance(p, pt)
                if dist < min:
                    min, min_pt = dist, p
            return min_pt

        # check if seg bbox contains ref
        seg_bbox = bbox(seg, self.threshold)
        if bbox_contains(ref, seg_bbox):
            # in that case, snap first to first
            # and second to second point
            snap = []
            # avoid invalid segments
            if seg[0] != nearest_point(seg[0], ref):
                snap.append([seg[0], nearest_point(seg[0], ref)])
            if seg[1] != nearest_point(seg[1], ref):
                snap.append([seg[1], nearest_point(seg[1], ref)])
            return snap

        # otherwise, there is common point
        max, max_pt = float('-Inf'), None
        for pt in seg:
            dist = ps_distance(pt, ref)
            if dist > max:
                max, max_pt = dist, pt
        snap = []
        snap.append([max_pt, nearest_point(pt, ref)])
        return snap

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

            # FIRST TEST
            # search for reference segments
            # intersecting segment bbox
            # enlarged by snapping threshold
            test_1 = []
            collinear = False # collinear flag
            seg_bbox = bbox(seg, self.threshold) # enlarged bbox
            for ref in self.reference:
                # bbox intersection
                if bbox_intersects(ref, seg_bbox):
                    test_1.append(ref)
                # check if ref bbox contains segment
                # if true, ignore segment (collinear)
                ref_bbox = bbox(ref, self.threshold)
                if bbox_contains(seg, ref_bbox):
                    collinear = True
                    break

            # if collinear, ignore
            if collinear: continue

            # if no refs, append without further test
            if not test_1:
                self.snapped.append(seg)
                continue
            # if only one, no further search required
            elif len(test_1) == 1:
                snap = self.snap(seg, test_1[0])
                self.snapped.extend(snap)
                continue

            # SECOND TEST
            # check for ref segments
            # "within" segment
            test_2 = []
            for ref in test_1:
                first, second = ref
                if ps_distance(first, seg) <= self.threshold**2 and \
                   ps_distance(second, seg) <= self.threshold**2:
                    test_2.append(ref)

            if not test_2:
                self.snapped.append(seg)
                continue
            # ignore more complicated checks
            elif len(test_2) >= 1:
                snap = self.snap(seg, test_2[0])
                self.snapped.extend(snap)
                continue

        # replace
        self.segments = self.snapped








