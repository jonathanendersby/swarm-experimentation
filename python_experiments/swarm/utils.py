
def lines_contain(lines, expect):
    # Returns True if any of the lines in the list include the expect string.
    for line in lines:
        # print('### ', line.decode('utf-8').strip())
        if expect in line.decode('utf-8'):
            return True

    return False


def line_containing(lines, expect):
    # Returns the first line to contain the expect string.
    for line in lines:
        # print('### ', line.decode('utf-8').strip())
        if expect in line.decode('utf-8'):
            return line.decode('utf-8')


def checksum(s):
    cs = 0
    h = s.encode()
    for c in h[1:]:
        cs = cs ^ c
    h = h + b'*%02X\n' % cs
    return h


class GPSStats:
    latitude = None
    longitude = None
    altitude = None
    course = None
    speed = None
    hdop = None
    vdop = None
    gnss_sats = None
    fix = None
    fix_type = None

    def __str__(self):
        return 'Swarm Tile GPS Fix (' + str(self.latitude) + ', ' + str(self.longitude) + ')'

    def verbose(self):
        out = 'Swarm Tile GPS Fix:\n'
        out += 'Latitude: ' + str(self.latitude) + '\n'
        out += 'Longitude: ' + str(self.longitude) + '\n'
        out += 'Altitude: ' + str(self.altitude) + ' meters\n'
        out += 'Course: ' + str(self.course) + ' degrees\n'
        out += 'Speed: ' + str(self.speed) + ' km/h\n'
        out += 'Horizontal Dilution of Precision: ' + str(self.hdop) + '\n'
        out += 'Vertical Dilution of Precision: ' + str(self.vdop) + '\n'
        out += 'GNSS Sats: ' + str(self.gnss_sats) + '\n'
        out += 'Fix: ' + str(self.fix) + '\n'
        out += 'Fix Type: ' + str(self.fix_type) + '\n'
        return out


GNSS_FIX_TYPES = {
    'NF': 'No Fix',
    'DR': 'Dead Reckoning',
    'G2': 'Standalone 2D',
    'G3': 'Standalone 3D',
    'D2': 'Differential 2D',
    'D3': 'Differential 3D',
    'RK': 'GNSS + Dead Reckoning',
    'TT': 'Time Only',
}