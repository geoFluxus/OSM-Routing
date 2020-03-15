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
xmin, xmax = bbox.xMinimum(), bbox.xMaximum()
ymin, ymax = bbox.yMinimum(), bbox.yMaximum()

# check if point lies within bbox
def in_bbox(point):
    x, y = point.x(), point.y()
    
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
        if in_bbox(point):
            # create feat
            feat = QgsFeature()
            feat.setGeometry(geom)
            provider.addFeature(feat)
            break
            
# publish check layer
checkLayer.commitChanges()
proj.addMapLayer(checkLayer)

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
for feat in checkLayer.getFeatures():
    geom = feat.geometry()
    
    # split to segments
    pts = list(geom.get())
    n = len(pts) - 1
    for i in range(n):
        start = (pts[i].x(), pts[i].y())
        end = (pts[i+1].x(), pts[i+1].y())
        seg = (start, end)
        check_segs.append(seg)
        
## side test
#def side(p, seg):
#    p1, p2 = seg
#    t1 = (p[0] - p1[0]) * (p2[1] - p1[1])
#    t2 = (p2[0] - p1[0]) * (p[1] - p1[1])
#    side = t1 - t2
#    if abs(side) <= 1e-07:
#        return 0
#    elif side > 0:
#        return 1
#    return -1


# dot product
def dot(v, w):
    dx = v[1][0] - v[0][0]
    dy = v[1][1] - v[0][0]
    d = (dx**2+dy**2)**0.5
    v = (dx/d, dy/d)
    
    dx = w[1][0] - w[0][0]
    dy = w[1][1] - w[0][0]
    d = (dx**2+dy**2)**0.5
    w = (dx/d, dy/d)
    
    prod = [vc*wc for vc, wc in zip(v, w)]
    return sum(prod)
    
# create final layer
finalLayer = QgsVectorLayer('Linestring', 'final', 'memory')
provider = finalLayer.dataProvider()
finalLayer.startEditing()

# remove equal segments
snap_set = set(snap_segs)
check_set = set(check_segs)
commons = snap_set.intersection(check_set)
for common in commons:
    snap_segs.remove(common)
    check_segs.remove(common)

# read also OPPOSITE DIRECTION!
snap_set = set(snap_segs)
check_set = set([cs[::-1] for cs in check_segs])
commons = snap_set.intersection(check_set)
for common in commons:
    snap_segs.remove(common)
    check_segs.remove(common[::-1])
    
segments = []
for ss in snap_segs:
    # segment bbox
    xr = sorted([ss[0][0], ss[1][0]])
    yr = sorted([ss[0][1], ss[1][1]])
    
    found = []
    for cs in check_segs:
        if ss[0] == cs[0]:
            if (cs[1][0] >= xr[0] and cs[1][0] <= xr[1]) and \
               (cs[1][1] >= yr[0] and cs[1][1] <= yr[1]):
                   found.append((ss[1], cs[1]))
        if ss[0] == cs[1]:
            if (cs[0][0] >= xr[0] and cs[0][0] <= xr[1]) and \
               (cs[0][1] >= yr[0] and cs[0][1] <= yr[1]):
                   found.append((ss[1], cs[0]))
        if ss[1] == cs[1]:
            if (cs[0][0] >= xr[0] and cs[0][0] <= xr[1]) and \
               (cs[0][1] >= yr[0] and cs[0][1] <= yr[1]):
                   found.append((ss[0], cs[0]))
        if ss[1] == cs[0]:
            if (cs[1][0] >= xr[0] and cs[1][0] <= xr[1]) and \
               (cs[1][1] >= yr[0] and cs[1][1] <= yr[1]):
                   found.append((ss[0], cs[1]))
    if not found:
        segments.append(ss)
    else:
        segments.extend(found)

#add features 
for seg in segments:
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
    
    
        