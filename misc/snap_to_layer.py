from qgis.core import (QgsProject, 
                       QgsFeature,
                       QgsVectorLayer,
                       QgsPoint,
                       QgsGeometry)

# initialize project
proj = QgsProject.instance()

# fetch layers
ways = proj.mapLayersByName('ways')[0]
simplified = proj.mapLayersByName('simplified')[0]

# compute bbox of simplified
bbox = simplified.extent()
print(bbox)
xmin, xmax = bbox.xMinimum(), bbox.xMaximum()
ymin, ymax = bbox.yMinimum(), bbox.yMaximum()

# check if point lies within bbox
def in_bbox(point):
    x, y = point
    
    if (x>=xmin and x<=xmax) and \
       (y>=ymin and y<=ymax):
           return True
    return False
    
# create check layer
checkLayer = QgsVectorLayer('Linestring', 'check', 'memory')
provider = checkLayer.dataProvider()
checkLayer.startEditing()

# fetch ways feats
# lying within the bbox
segments = []
for feat in ways.getFeatures():
    geom = feat.geometry()
    # if only one point
    for point in geom.get():
        if in_bbox((point.x(), point.y())):
            # create feat
            feat = QgsFeature()
            feat.setGeometry(geom)
            provider.addFeature(feat)
            break
            
# publish check layer
checkLayer.commitChanges()
#proj.addMapLayer(checkLayer)

# recover check vertices
vertices = set()
for feat in checkLayer.getFeatures():
    geom = feat.geometry()
    for pt in geom.get():
        vex = (pt.x(), pt.y())
        vertices.add(vex)
        
# compute distance between points
def point_distance(pt, vex):
    dx = vex[0] - pt[0]
    dy = vex[1] - pt[1]
    return dx**2 + dy**2
        
        
# create snap layer
snapLayer = QgsVectorLayer('Linestring', 'snap', 'memory')
provider = snapLayer.dataProvider()
snapLayer.startEditing()

# STEP 1: SNAP POINTS
# iterate simplified features
thres = 0.01**2 # in degrees
for feat in simplified.getFeatures():
    geom = feat.geometry()
    
    pts = []
    for point in geom.get():
        pt = (point.x(), point.y())
       
        # iterate check vertices
        found = False
        for vex in vertices:
            if point_distance(pt, vex) <= thres:
                pts.append(QgsPoint(vex[0], vex[1]))
                found = True
                break
                
        if not found:
            pts.append(QgsPoint(pt[0], pt[1]))
    
    # create feature
    feat = QgsFeature()
    feat_geom = QgsGeometry.fromPolyline(pts)
    if feat_geom.length() != 0:
        feat.setGeometry(feat_geom)
        provider.addFeature(feat)
    
# publish snap layer
snapLayer.commitChanges()
proj.addMapLayer(snapLayer)


# STEP 2: SNAP EDGES
# split snap feats to segments
snap_segs = []
for feat in snapLayer.getFeatures():
    geom = feat.geometry()
    
    pts = list(geom.get())
    n = len(pts) - 1
    for i in range(n):
        start = (pts[i].x(), pts[i].y())
        end = (pts[i+1].x(), pts[i+1].y())
        seg = (start, end)
        snap_segs.append(seg)
        
# split check feats to segments
check_segs = []
border_points = []
for feat in checkLayer.getFeatures():
    geom = feat.geometry()
    
    # split to segments
    pts = list(geom.get())
    n = len(pts) - 1
    for i in range(n):
        start = (pts[i].x(), pts[i].y())
        end = (pts[i+1].x(), pts[i+1].y())
        border_points.append(start)
        border_points.append(end)
        seg = (start, end)
        check_segs.append(seg)

# border points of checkLayer
border_points = [pt for pt in border_points \
                 if border_points.count(pt) == 1]
borderLayer = QgsVectorLayer('Point', 'border', 'memory')
provider = borderLayer.dataProvider() 
borderLayer.startEditing()
for pt in border_points:
    feat = QgsFeature()
    feat_geom = QgsPoint(pt[0], pt[1])
    feat.setGeometry(feat_geom)
    provider.addFeature(feat)
borderLayer.commitChanges()
#proj.addMapLayer(borderLayer)

# create final layer
finalLayer = QgsVectorLayer('Linestring', 'final', 'memory')
provider = finalLayer.dataProvider()
finalLayer.startEditing()
    
# side test
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
    
# intersect test
def intersect(s_a, s_b):
    side_a = side(s_a[0], s_b)
    side_b = side(s_a[1], s_b)
    side_c = side(s_b[0], s_a)
    side_d = side(s_b[1], s_a)
    if (side_a != side_b) and \
       (side_c != side_d):
           return True
    return False
    
def dist(seg, pt):
    p1, p2 = seg
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = pt
    
    px = x2 - x1
    py = y2 - y1

    norm = px*px + py*py
    if norm == 0: return -1
    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(norm)

    if u > 1 or u < 0:
        return -1

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    dist = dx * dx + dy * dy

    return dist


segments = []
# iterate to be snapped
for ss in snap_segs:
    if ss in check_segs or \
       ss[::-1] in check_segs: continue
    
    found = []
    for cs in check_segs:
        first, second = cs
        if intersect(ss, cs) or \
           dist(ss, first) <= thres or \
           dist(ss, second) <= thres:
            found.append(cs)
    
    if not found:
        segments.append(ss)
    else:
        x = [pt[0] for pt in ss]
        x.sort()
        xmin, xmax = x
        xmin -= thres**0.5 / 2.0
        xmax += thres**0.5 / 2.0
        y = [pt[1] for pt in ss]
        y.sort()
        ymin, ymax = y
        ymin -= thres**0.5 / 2.0
        ymax += thres**0.5 / 2.0
        
        checks = []
        for seg in found:
            p1, p2 = seg
            if (in_bbox(p1) and p1 not in ss) or \
               (in_bbox(p2) and p2 not in ss):
                checks.append(seg)
        
        if len(checks) == 0:
            p1, p2 = ss
            oh = False
            for seg in found:
                x = [pt[0] for pt in seg]
                x.sort()
                xmin, xmax = x
                xmin -= thres**0.5 / 2.0
                xmax += thres**0.5 / 2.0
                y = [pt[1] for pt in seg]
                y.sort()
                ymin, ymax = y
                ymin -= thres**0.5 / 2.0
                ymax += thres**0.5 / 2.0
                if (in_bbox(p1) and p1 not in seg) or \
                   (in_bbox(p2) and p2 not in seg):
                    oh = True
                    break
            if oh: continue
            segments.append(ss)
        if len(checks) == 1:
            pts = []
            pts.extend(ss)
            pts.extend(checks[0])
            pts.sort(key=lambda pt: pt[0])
            #pts.sort(key=lambda pt: pt[1])
            for i in range(3):
                segments.append((pts[i], pts[i+1]))

#add features 
for seg in segments:
    if seg[0] == seg[1]: continue
    feat = QgsFeature()
    start = QgsPoint(seg[0][0], seg[0][1])
    end = QgsPoint(seg[1][0], seg[1][1])
    pts = [start, end]
    feat_geom = QgsGeometry.fromPolyline(pts)
    feat.setGeometry(feat_geom)
    provider.addFeature(feat)
    
# publish final layer
finalLayer.commitChanges()
proj.addMapLayer(finalLayer)
    
    
        