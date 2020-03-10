# export point layer (.csv)
def export_points(points, path, name):
    filename = path + '/' + name + '.csv'
    fil = open(filename, 'w')
    fil.write('wkt\n')
    for point in points:
        lat, lon = point
        row = 'POINT({} {})\n'.format(lon, lat)
        fil.write(row)
    fil.close()

# export line layer (.csv)
def export_lines(lines, path, name):
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