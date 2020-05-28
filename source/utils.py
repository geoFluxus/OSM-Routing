from __future__ import print_function
import builtins as __builtin__
import time


def print(*args, **kwargs):
    local_time = time.localtime()
    __builtin__.print(time.strftime('%a, %d %b %Y %H:%M:%S', local_time), end=": ")
    return __builtin__.print(*args, **kwargs)


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
def export_lines(path, name, lines, epsg):
    from pyproj import CRS
    crs = CRS.from_epsg(epsg)
    unit = str(crs.axis_info[0])
    reverse = False  # degree-unit crs have reverse coord order
    if 'degree' in unit: reverse = True

    filename = path + '/' + name + '.csv'
    fil = open(filename, 'w')
    fil.write('wkt\n')
    for line in lines:
        row = 'LINESTRING('
        for point in line:
            if reverse:
                lat, lon = point
            else:
                lon, lat = point
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

