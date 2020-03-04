from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterVectorDestination,
                       QgsMessageLog,
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


class SimplifyNetwork(QgsProcessingAlgorithm):
    INPUT_LAYER = 'INPUT_LAYER'
    OUTPUT_LAYER = 'OUTPUT_LAYER'
    
    def __init__(self):
        super().__init__()
        
    def name(self):
        return "SimplifyNetwork"
        
    def tr(self, text):
        return QCoreApplication.translate("SimplifyNetwork", text)
        
    def displayName(self):
        return self.tr("Simplify OSM Network")
        
    def group(self):
        return self.tr("OSMAlgs")
        
    def groupId(self):
        return "OSMAlgs"
        
    def shortHelpString(self):
        return self.tr("Simplify OSM network for pgRouting")
        
    def helpUrl(self):
        return "https://qgis.org"
        
    def createInstance(self):
        return type(self)()
        
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.INPUT_LAYER,
            self.tr("Input Layer"),
            [QgsProcessing.TypeVectorAnyGeometry]))
        self.addParameter(QgsProcessingParameterVectorDestination(
            self.OUTPUT_LAYER,
            self.tr("Output Layer")
        ))
        
        def processAlgorithm(self, parameters, context, feedback):
            input_layer = self.parameterAsVectorLayer(parameters, self.INPUT_LAYER, context)
            output_layer = self.parameterAsOutputLayer(parameters, self.OUTPUT_LAYER, context)
            
            results = {}
            results[self.OUTPUT_LAYER] = output_layer
            return results


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
new_graph = {} # Graph of new network
grouped = {} # Initialize groups
for inter, is_inter in inters.items():
    # Not an intersection, skip
    if not(is_inter): continue
    
    # Include inter to new graph
    new_graph[inter] = []
    grouped[inter] =  False
    
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
        
        # Add as edge to vertex
        new_graph[inter].append(fet_geom)

# Publish SEGMENTS layer
segmentLayer.commitChanges()
proj.addMapLayer(segmentLayer)



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
inters = list(new_graph.keys())
num = len(inters)
groups, gnum = [], 0
thres = 0.001
fet = QgsFeature()
fet.setFields(fields)
for i in range(num):
    orig = inters[i]
    if grouped[orig]: continue
    
    # Add as layer feature
    point = QgsPointXY(orig[0], orig[1])
    fet.setGeometry(QgsGeometry.fromPointXY(point))
    fet.setAttribute('group', gnum)
    provider.addFeatures([fet])
    
    group = [orig]
    grouped[orig] = True
    for j in range(i+1, num):
        dest = inters[j]
        if grouped[dest]: continue
        
        dist = compute_dist(orig, dest)
        if dist <= thres**2:
            group.append(dest)
            grouped[dest] = True
            
            # Add as layer feature
            point = QgsPointXY(dest[0], dest[1])
            fet.setGeometry(QgsGeometry.fromPointXY(point))
            fet.setAttribute('group', gnum)
            provider.addFeatures([fet])
            
    groups.append(group)
    gnum += 1
    
# Publish INTESECTIONS layer
interLayer.commitChanges()
proj.addMapLayer(interLayer)
    
# Create grid
# to layer extend
#ext = segmentLayer.extent()
#res = 0.01
#height = int(ext.height() / res) + 1
#idth = int(ext.width() / res) + 1
#xmin, ymin = ext.xMinimum(), ext.yMinimum()

#gridLayer = QgsVectorLayer("Point", "grid", "memory")
#provider = gridLayer.dataProvider()
#gridLayer.startEditing()
#for w in range(width):
    #for h in range(height):
        #fet = QgsFeature()
        #point = QgsPointXY(xmin + w*res, ymin + h*res)
        #fet.setGeometry(QgsGeometry.fromPointXY(point))
        #provider.addFeatures([fet])
#gridLayer.commitChanges()
#proj.addMapLayer(gridLayer)

        




