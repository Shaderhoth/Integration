import serial
import logging

_LOGGER = logging.getLogger(__name__)

class RadarReader:
    def __init__(self, device_path):
        self.device_path = device_path
        self.serial_connection = None

    def connect(self):
        try:
            self.serial_connection = serial.Serial(self.device_path, baudrate=115200, timeout=1)
            _LOGGER.info("Connected to radar at %s", self.device_path)
        except serial.SerialException as e:
            _LOGGER.error("Failed to connect to radar: %s", e)
            self.serial_connection = None

    def read_data(self):
        if not self.serial_connection:
            self.connect()
        if self.serial_connection:
            try:
                line = self.serial_connection.readline().decode("utf-8").strip()
                if line:
                    return int(line) 
            except Exception as e:
                _LOGGER.error("Error reading radar data: %s", e)
        return None
