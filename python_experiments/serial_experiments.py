from swarm.tile import TileSerial
import settings


tile = TileSerial()
tile.connect(settings.SWARM_TILE_PORT)
tile.set_logging(True)
tile.write_read('$DT 0', expect='$DT OK')  # Turn off datetime unsolicited messages
tile.write_read('$GN 0', expect='$GN OK')  # Turn off GNSS unsolicited messages

print('Tile Firmware Version:')
print(tile.get_firmware_version())

print('Current GPS Time (UTC):')
print(tile.get_gps_time())
print('')
gps_stats = tile.get_gps_stats()
print(gps_stats.verbose())
print(tile.get_message_count(), 'unread messages.')

print('\n10 second monitor:')
tile.read_monitor(seconds=10)

# message = '$TD "Hello World From Python Via Direct Serial!!"'