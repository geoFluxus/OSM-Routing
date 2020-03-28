# export point layer (.csv)
def export_points(path, name, points, attrs=[]):
    filename = path + '/' + name + '.csv'
    fil = open(filename, 'w')
    fil.write('wkt;attr\n')
    for point, attr in zip(points, attrs):
        lat, lon = point
        row = 'POINT({} {});{}\n'.format(lon, lat, attr)
        fil.write(row)
    fil.close()

# export line layer (.csv)
def export_lines(path, name, lines):
    filename = path + '/' + name + '.csv'
    fil = open(filename, 'w')
    fil.write('wkt\n')
    for line in lines:
        row = 'LINESTRING('
        for point in line:
            lat, lon = point
            row += '{} {},'.format(lon, lat)
        row = row[:-1] + ')\n'
        fil.write(row)
    fil.close()

# ask (yes/no) input
def ask_input(question):
    resp = ''
    while resp.lower() not in ['y', 'n']:
        resp = input('{}? [Y/N] '.format(question.capitalize()))
    if resp == 'y':
        return True
    else:
        return False

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

