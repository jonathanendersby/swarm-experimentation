import telnetlib
import time

# Heavily referencing
# https://swarm.space/wp-content/uploads/2021/07/Swarm-Tile-Product-Manual.pdf
# https://swarm.space/wp-content/uploads/2021/08/Swarm-Eval-Kit-Quickstart-Guide.pdf

SWARM_EVAL_HOST = "192.168.30.30"


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


def expect_okay(_data):
    lines = data.split('\n')
    for line in lines:
        if "$TD OK" in line:
            return True

    return False


def checksum(s):
    cs = 0
    h = s.encode()
    for c in h[1:]:
        cs = cs ^ c
    h = h + b'*%02X\n'%cs
    return h


if __name__ == "__main__":
    try:

        tn = telnetlib.Telnet(SWARM_EVAL_HOST, timeout=10)
        print('Connected to', SWARM_EVAL_HOST)

        # Get some data to see if we have GPS / RSSI etc.
        data = relaxed_read(tn)

        # Send Message
        message = '$TD "Hello World From Python!!"'
        checksummed_message = checksum(message)
        print(checksummed_message)

        tn.write(checksummed_message)
        data = relaxed_read(tn)
        print(data)
        sent = expect_okay(data)
        print('Message Send Result:', sent)

    except Exception as e:
        print('Exception Triggered')
        print(e)

    finally:
        print('Disconnecting...')
        tn.close()
        time.sleep(0.1)

