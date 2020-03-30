# point-point distance
def pp_distance(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx**2 + dy**2


# explode linestring geometry
def explode(geometry):
    exploded = []
    for line in geometry:
        n = len(line) - 1
        for i in range(n):
            segment = [line[i], line[i+1]]
            exploded.append(segment)
    return exploded


# compute geometry extent
def extent(geometry):
    xmin, ymin = float('Inf'), float('Inf')
    xmax, ymax = float('-Inf'), float('-Inf')
    for segment in geometry:
        for pt in segment:
            # lat, lon ordering
            if pt[1] <= xmin:
                xmin = pt[1]
            if pt[1] >= xmax:
                xmax = pt[1]
            if pt[0] <= ymin:
                ymin = pt[0]
            if pt[0] >= ymax:
                ymax = pt[0]
    return xmin, ymin, xmax, ymax


# segment bbox
def bbox(seg, grow=0.0):
    # compute xmin, xmax
    x = [pt[0] for pt in seg]
    x.sort()
    xmin, xmax = x
    xmin -= grow / 2.0
    xmax += grow / 2.0

    # compute ymin, ymax
    y = [pt[1] for pt in seg]
    y.sort()
    ymin, ymax = y
    ymin -= grow / 2.0
    ymax += grow / 2.0

    return xmin, ymin, xmax, ymax


# point in bbox
def in_bbox(pt, bbox):
    xmin, ymin, xmax, ymax = bbox
    x, y = pt
    if (xmin <= x <= xmax) and \
       (ymin <= y <= ymax):
        return True
    return False


# bbox intersects
def bbox_intersects(seg, bbox):
    p1, p2 = seg
    if in_bbox(p1, bbox) or \
       in_bbox(p2, bbox):
        return True
    return False


# bbox contains
def bbox_contains(seg, bbox):
    p1, p2 = seg
    if in_bbox(p1, bbox) and \
       in_bbox(p2, bbox):
        return True
    return False


# side test for point-segment
def side(p, seg):
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
def intersects(s_a, s_b):
    side_a = side(s_a[0], s_b)
    side_b = side(s_a[1], s_b)
    side_c = side(s_b[0], s_a)
    side_d = side(s_b[1], s_a)
    if (side_a != side_b) and \
       (side_c != side_d):
        return True
    return False


# point-segment distance
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
    # if norm == 0: return float('Inf')

    # compute parameter
    u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)

    # point lies "outside" of segment
    # also ignore
    if u > 1 or u < 0: return float('Inf')

    # line parametric equations
    # to compute point projection on segment
    x = x1 + u * px
    y = y1 + u * py

    # compute distance vector
    # between point and projection
    dx = x - x3
    dy = y - y3

    return dx * dx + dy * dy