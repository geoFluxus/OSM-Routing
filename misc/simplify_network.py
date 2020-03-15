from qgis.core import (QgsMessageLog,
                       QgsWkbTypes,
                       QgsPoint,
                       QgsPointXY,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsGeometry,
                       QgsProject,
                       QgsFeatureRequest,
                       QgsTopologyPreservingSimplifier,
                       QgsField)
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.utils import iface

# Initialize QGIS project
proj = QgsProject.instance()

# Create graph
# { vertex : adjacent_edges}
graph = {}

# Keep track of processed edges
processed = {}

# Fetch OSM layer & features
inputLayer = iface.activeLayer()
feats = inputLayer.getFeatures()

# Build graph
for feat in feats:
    # Retrieve LineString geometry
    geom = feat.geometry()
    string = geom.get()
    
    # Split into segments
    n = len(string) - 1
    segments = []
    for i in range(n):
        start, end = string[i], string[i+1]
        segment = QgsGeometry.fromPolyline([start, end])
        segments.append(segment)
        
    # Process segments
    for segment in segments:
        processed[segment] = False # Mark edge as not processed
        for vex in segment.get():
            coords = (vex.x(), vex.y())
            if coords not in graph.keys():
                graph[coords] = [segment]
            else:
                graph[coords].append(segment)
           
           
# Check if graph vertex is intersection
def is_intersection(vex, edges):
    # TEST 1
    # Check if vertex is an orphan point
    # (part of only one edge)
    if len(edges) == 1:
        # Start/ end points of edge
        geom = edges[0].get()
        start, end = geom[0], geom[-1]
        
        # Check if vertex is equal to
        # start or end point
        x, y = vex[0], vex[1]
        if (x == start.x() and y == start.y()) or \
           (x == end.x() and y == end.y()):
            return True
    
    # TEST 2
    # More than two adjacent edges == intersection !
    if len(edges) > 2:
        return True
        
    return False


# Record intersections
inters = {}
for vex, edges in graph.items():
    if is_intersection(vex, edges):
        # Append intersection
        inters[vex] = True
    else:
        inters[vex] = False


# Create SEGMENTS layer
segmentLayer = QgsVectorLayer("LineString", "segments", "memory")
provider = segmentLayer.dataProvider()
segmentLayer.startEditing()

# Reverse edge
def reverse_edge(edge):
    geom = list(edge.get())
    pts = [pt for pt in geom[::-1]]
    return QgsGeometry.fromPolyline(pts)

# Traverse intersections
for inter, is_inter in inters.items():
    # Not an intersection, skip
    if not(is_inter): continue
    
    # Traverse all edges of the intersection!
    edges = graph[inter]
    for edge in edges:
        # Edge processed, skip
        if processed[edge]: continue
        
        # Start search
        STOP = False
        
        # Start point sequence with intersection
        pts = [QgsPoint(inter[0], inter[1])]
        
        # Jump from edge to edge
        # till reaching an intersection
        curr_pos = inter
        curr_edge = edge
        while not(STOP):
            # Get edge geometry
            geom = curr_edge.get()
            
            # Check start point of edge
            # If different from intersection, reverse the edge
            # The current intersection should always be the starting point!
            start = (geom[0].x(), geom[0].y())
            if start != curr_pos:
                reverse = reverse_edge(curr_edge)
                geom = reverse.get()
                start = (geom[0].x(), geom[0].y())
                if start != curr_pos:
                    break
               
            # Traverse edge
            for pt in list(geom)[1:]: # The intersection has been added!
                # Collect point
                pts.append(pt)
                
                # If intersection == STOP!
                curr_pos = (pt.x(), pt.y())
                if inters[curr_pos]:
                    STOP = True
                    break
                
            # Mark edge as processeds
            processed[curr_edge] = True
            
            # Jump to next edge
            # with end point of current edge
            adjacent = graph[curr_pos]
            for adj in adjacent:
                if not(processed[adj]):
                    curr_edge = adj
                    break
        
        # Add as layer feature
        fet = QgsFeature()
        fet_geom = QgsGeometry.fromPolyline(pts)
        fet.setGeometry(fet_geom)
        provider.addFeatures([fet])

# Publish SEGMENTS layer
segmentLayer.commitChanges()
proj.addMapLayer(segmentLayer)


# Build new graph
graph = {}
grouped = {} # Mark as grouped
feats = segmentLayer.getFeatures()
for feat in feats:
    geom = feat.geometry()
    pts = geom.get()
    
    # Now, each edge has as edge points
    # ALWAYS intersections!!!
    for vex in [pts[0], pts[-1]]:
        coords = (vex.x(), vex.y())
        if coords in graph.keys():
            graph[coords].append(geom)
        else:
            graph[coords] = [geom]
            grouped[coords] = False


# Create INTESECTIONS layer
interLayer = QgsVectorLayer("Point", "intersections", "memory")
provider = interLayer.dataProvider()
provider.addAttributes([QgsField('group', QVariant.Int)])
interLayer.updateFields()
fields = interLayer.fields()
interLayer.startEditing()

def compute_dist(o, d):
    dx = d[0] - o[0]
    dy = d[1] - o[1]
    return dx**2 + dy**2
    
# Iterate intersections
inters = list(graph.keys())
num = len(inters)
groups, gnum = [], 0
thres = 0.01
for i in range(num):
    orig = inters[i]
    if grouped[orig]: continue
    
    # Form group by distance
    group = []
    for j in range(i, num):
        dest = inters[j]
        if grouped[dest]: continue
        
        dist = compute_dist(orig, dest)
        if dist <= thres**2:
            group.append(dest)
            grouped[dest] = True
            
            # Add as layer feature
            fet = QgsFeature()
            fet.setFields(fields)
            point = QgsPointXY(dest[0], dest[1])
            fet.setGeometry(QgsGeometry.fromPointXY(point))
            fet.setAttribute('group', gnum)
            provider.addFeatures([fet])
    
    groups.append(group)
    gnum += 1
    
# Publish INTESECTIONS layer
interLayer.commitChanges()
proj.addMapLayer(interLayer)


def compute_centroid(group):
    if len(group) >= 2:
        n = len(group)
        x = sum([pt[0] for pt in group])
        y = sum([pt[1] for pt in group])
        return x / n, y / n
    else:
        return group[0]

# Process groups
centroid_graph = {}
for group in groups:
    # Compute centroid
    centroid = compute_centroid(group)
    
    # Collect all related edges
    edges = set()
    for inter in group:
        inter_edges = graph[inter]
        edges.update(inter_edges)
        #print(new_graph[inter])
        #for edge in new_graph[inter]:
            #points = []
            #for point in edge.get():
                #points.append((point.x(), point.y()))
            #edges.add(tuple(points))
    
    # Add to graph
    centroid_graph[centroid] = edges

# Form centroid connections
connections = {}
centroids = list(centroid_graph.keys())
num = len(centroids)
for i in range(num):
    curr_centroid = centroids[i]
    curr_edges = centroid_graph[curr_centroid]
    connections[curr_centroid] = []
    
    for j in range(i+1, num):
        other_centroid = centroids[j]
        edges = centroid_graph[other_centroid]
        common = edges.intersection(curr_edges)
        if len(common) > 0:
            connections[curr_centroid].append(other_centroid)
            
            
# Create SIMPLIFIED layer
simplifiedLayer = QgsVectorLayer("LineString", "simplified", "memory")
provider = simplifiedLayer.dataProvider()
simplifiedLayer.startEditing()

for orig, dests in connections.items():
    for dest in dests:
        # Define geometry
        o_p = QgsPoint(orig[0], orig[1])
        e_p = QgsPoint(dest[0], dest[1])
        pts = [o_p, e_p]
        
        # Add as layer feature
        fet = QgsFeature()
        fet_geom = QgsGeometry.fromPolyline(pts)
        fet.setGeometry(fet_geom)
        provider.addFeatures([fet])

# Publish SIMPLIFIED layer
simplifiedLayer.commitChanges()
proj.addMapLayer(simplifiedLayer)
        
    