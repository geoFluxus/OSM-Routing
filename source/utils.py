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