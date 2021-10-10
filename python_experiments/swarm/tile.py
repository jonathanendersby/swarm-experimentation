import serial
import time
import datetime
import pytz
from .utils import *


class TileSerial:
    connection = None
    logging = False
    log_file = None

    def __init__(self):
        pass

    def set_logging(self, _bool):
        self.logging = _bool

    def log_write(self, message, annotation):
        try:
            check = message.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            check = str(message)

        if check.strip() != '':
            if self.logging:
                if self.log_file is None:
                    self.log_file = open('tile.log', 'a')

                try:
                    m = message.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    m = str(message) + '\n'

                self.log_file.write(datetime.datetime.now().isoformat() + ' ' + str(annotation) * 3 + ' ' + m)
                self.log_file.flush()

    class NoExpectedResponse(Exception):
        pass

    def connect(self, port):
        self.connection = serial.Serial(port, baudrate=115200)
        self.connection.timeout = 2
        self.log_write('Tile Serial Connected on' + port, annotation='#')

    def read_monitor(self, seconds):
        # Helpful for printing out the output for a few seconds
        start = datetime.datetime.now()
        while True:
            r = self.connection.read_until()
            self.log_write(r, annotation='<')
            _lines = [r]

            if (datetime.datetime.now() - start).total_seconds() > seconds:
                break

    def read_expectantly(self, expect):
        # Reads until we receive a full message containing the string passed in `expect`

        # Optimistically try a cheeky read_until
        r = self.connection.read_until()
        self.log_write(r, annotation='<')
        _lines = [r]

        if lines_contain(_lines, expect):
            # We got what we wanted, let's return
            return line_containing(_lines, expect)

        else:
            # Okay, we didn't get what we expected from the first line, so let's see if
            # there's more in the buffer

            if self.connection.in_waiting:
                # Yes, there's more in the buffer, lets read it all and see if any of that matches.
                while self.connection.in_waiting:
                    # We have to do this in case there's a ton of messages that need to be received.
                    # Can't just assume 3 tries will do it (see below)
                    r = self.connection.read_until()
                    self.log_write(r, annotation='<')
                    _lines.append(r)

            if lines_contain(_lines, expect):
                # We got what we wanted, let's return
                return line_containing(_lines, expect)

            # The buffer is empty but we still haven't received what we wanted, lets wait 200ms
            for i in range(1, 3):
                self.log_write('Read Retry' + ' #' + str(i), annotation='#')
                r = self.connection.read_until()
                self.log_write(r, annotation='<')
                _lines.append(r)
                if lines_contain(_lines, expect):
                    break

                time.sleep(0.2)

            if lines_contain(_lines, expect):
                return line_containing(_lines, expect)
            else:
                raise self.NoExpectedResponse

    def write_read(self, message, expect=None):
        # Writes a message and returns the first list containing the expect string.
        # If expect is not set, returns the first line.

        message = checksum(message)
        self.connection.write(message)
        self.log_write(message, annotation='>')
        if expect:
            r = self.read_expectantly(expect)
        else:
            r = self.connection.read_until().decode('utf-8')

        return r

    def get_gps_time(self):
        # Returns a timezone Naive Datetime.Datetime from the GPS data, or None
        # if GPS time is unavailable.
        # b'$DT 2021 10 10 10:06 48,V*40\n'
        self.write_read('$DT 1', expect='$DT OK')  # Trigger an unsolicited message
        line = self.write_read('$DT @', expect='$DT ')
        self.write_read('$DT 0', expect='$DT OK')  # Turn off unsolicited datetime messages

        if line.startswith('$DT '):
            line = line[4:-6]
            _obj = datetime.datetime.strptime(line, '%Y%m%d%H%M%S')
            _obj = _obj.replace(tzinfo=pytz.UTC)
            return _obj

        # Whoops, nothing valid apparently?
        return None

    def get_gps_stats(self):
        # Returns a GPSStats object

        gps_stats = GPSStats()
        self.write_read('$GN 1', expect='$GN OK')
        line = self.write_read('$GN @', expect='$GN ')
        self.write_read('$GN 0', expect='$GN OK')

        values = line[4:-4].split(',')
        gps_stats.latitude = values[0]
        gps_stats.longitude = values[1]
        gps_stats.altitude = values[2]
        gps_stats.course = values[3]
        gps_stats.speed = values[4]

        self.write_read('$GS 1', expect='$GS OK')
        line = self.write_read('$GS @', expect='$GS ')
        self.write_read('$GS 0', expect='$GS OK')
        values = line[4:-4].split(',')
        gps_stats.hdop = values[0]
        gps_stats.vdop = values[1]
        gps_stats.gnss_sats = values[2]
        gps_stats.fix = str(values[4])
        gps_stats.fix_type = GNSS_FIX_TYPES.get(gps_stats.fix)

        return gps_stats

    def get_message_count(self, unread_only=False):
        # Returns the count (int) of messages on the tile
        if unread_only:
            line = self.write_read('$MM C=U', expect='$MM ')
        else:
            line = self.write_read('$MM C=*', expect='$MM ')
        count = line[4:-4]
        return int(count)

    def get_firmware_version(self):
        # Returns the firmware version
        return self.write_read('$FV', expect='$FV ')


