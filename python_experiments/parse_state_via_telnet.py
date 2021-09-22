import telnetlib
import time

# Heavily referencing
# https://swarm.space/wp-content/uploads/2021/07/Swarm-Tile-Product-Manual.pdf
# https://swarm.space/wp-content/uploads/2021/08/Swarm-Eval-Kit-Quickstart-Guide.pdf

SWARM_EVAL_HOST = "192.168.146.30"


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


def relaxed_read(_tn, seconds=5):
    time.sleep(0.1)
    out = _tn.read_until(match=b'EXIT_NOT_GOING_TO_HAPPEN', timeout=seconds).decode('ascii')
    time.sleep(0.1)
    return out


def clean_overlap(_string):
    # Look in the string to see if we have a $ at position > 0 which would
    # indicate that we received more than one response on the same line.

    if _string.index('$') and _string.index('$') > 0:
        return _string.split('$')[0]

    return _string()


def parse_state(_data, _state=None):

    if _state is None:
        _state = dict()

    lines = data.split('\n')
    for line in lines:
        # print(line)

        if line.startswith('$RT RSSI'):
            # Receive Test
            _state['RSSI'] = line[9:-3]

        elif line.startswith('$DT'):
            # Date Time Status
            # ,V = Valid Date Time, I = Invalid Date Time - Ignoring this for now.
            _state['datetime'] = line[4:-5]

        elif line.startswith('$GN'):
            # Geospatial Information
            # <latitude>,<longitude>,<altitude>, <course>,<speed>*xx
            values = line[4:-3].split(',')
            _state['latitude'] = values[0]
            _state['longitude'] = values[1]
            _state['altitude'] = values[2]
            _state['course'] = values[3]
            _state['speed'] = values[4]

        elif line.startswith('$GS'):
            # GPS Fix Quality
            # <hdop>,<vdop>,<gnss_sats>,<unused>,<fix>
            values = line[4:-3].split(',')
            _state['hdop'] = values[0]
            _state['vdop'] = values[1]
            _state['gnss_sats'] = values[2]
            _state['fix'] = values[4]
            _state['fix_type'] = GNSS_FIX_TYPES.get(_state['fix'])

        elif line.startswith('SOL: '):
            # SOL: 1.128V 0.0A$RT RSSI=-88*2d
            line = clean_overlap(line)
            values = line[5:].split(' ')
            _state['solar_voltage'] = values[0]
            _state['solar_current'] = values[1]

        elif line.startswith('3V3: '):
            # 3V3: 3.376V 0.056A$DT 20210909102029,V*43
            line = clean_overlap(line)
            values = line[5:].split(' ')
            _state['3V3_voltage'] = values[0]
            _state['3V3_current'] = values[1]

        elif line.startswith('BAT: '):
            # BAT: 3.992V 0.156A$DT 20210909102604,V*4a
            line = clean_overlap(line)
            values = line[5:].split(' ')
            _state['battery_voltage'] = values[0]
            _state['battery_current'] = values[1]

    return _state


if __name__ == "__main__":
    try:
        tn = telnetlib.Telnet(SWARM_EVAL_HOST, timeout=10)
        print('Connected to', SWARM_EVAL_HOST)

        # Get some data to see if we have GPS / RSSI etc.
        data = relaxed_read(tn)

        # Get Solar Stats
        state = parse_state(data)
        tn.write(b"@show solar\n")
        data = relaxed_read(tn)
        state = parse_state(data, _state=state)

        # Get 3v3 Stats
        tn.write(b"@show 3v3\n")
        data = relaxed_read(tn)
        state = parse_state(data, _state=state)

        # Get Battery Stats
        tn.write(b"@show battery\n")
        data = relaxed_read(tn)
        state = parse_state(data, _state=state)
        print(state)

    except Exception as e:
        print('Exception Triggered')
        print(e)

    finally:
        print('Disconnecting...')
        tn.close()
        time.sleep(0.1)

