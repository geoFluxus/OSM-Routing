class WKTparser():
    def __init__(self, filename):
        self.filename = filename
        self.segments = []

    def readfile(self):
        # Open file
        try:
            with open(self.filename) as f:
                rows = sum(1 for _ in f)
            fil = open(self.filename, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('File not found...')

        line = fil.readline()
        row = 1
        while line:
            progress = row / rows * 100
            print('Progress: {:.1f}%'.format(progress), end="\r", flush=True)

            segment = []
            if line.startswith('LINESTRING'):
                pts = line.strip('LINESTRING(')\
                          .strip(')\n')\
                          .split(',')
                for pt in pts:
                    geom = pt.split(' ')
                    geom = [float(coord) for coord in geom]
                    geom.reverse()
                    segment.append(tuple(geom))
                self.segments.append(segment)

            # proceed
            row += 1
            line = fil.readline()

        # CLOSE file
        fil.close()