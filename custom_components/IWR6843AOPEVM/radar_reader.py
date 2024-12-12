import serial
import logging
import threading
import time

_LOGGER = logging.getLogger(__name__)

class RadarReader:
    def __init__(self, cli_device_path, data_device_path):
        self.cli_device_path = cli_device_path
        self.data_device_path = data_device_path
        self.cli_connection = None
        self.data_connection = None
        self.people_count = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        self.connect_cli()
        self.connect_data()

        if self.data_connection:
            self.read_thread = threading.Thread(target=self.read_data_loop, daemon=True)
            self.read_thread.start()

    def connect_cli(self):
        try:
            self.cli_connection = serial.Serial(
                self.cli_device_path,
                baudrate=115200,
                timeout=1
            )
            _LOGGER.info("Connected to radar CLI port at %s", self.cli_device_path)
        except serial.SerialException as e:
            _LOGGER.error("Failed to connect to radar CLI port: %s", e)
            self.cli_connection = None

    def connect_data(self):
        try:
            self.data_connection = serial.Serial(
                self.data_device_path,
                baudrate=115200,
                timeout=1
            )
            _LOGGER.info("Connected to radar Data port at %s", self.data_device_path)
        except serial.SerialException as e:
            _LOGGER.error("Failed to connect to radar Data port: %s", e)
            self.data_connection = None

    def send_command(self, command):
        if self.cli_connection and self.cli_connection.is_open:
            try:
                self.cli_connection.write((command + '\n').encode('utf-8'))
                _LOGGER.debug(f"Sent command: {command}")
                response = self.cli_connection.readline().decode('utf-8').strip()
                _LOGGER.debug(f"Received response: {response}")
                return response
            except Exception as e:
                _LOGGER.error("Error sending command to radar CLI port: %s", e)
        else:
            _LOGGER.error("CLI connection is not open")
        return None


    def read_data_loop(self):
        while not self._stop_event.is_set():
            if self.data_connection and self.data_connection.is_open:
                try:
                    line = self.data_connection.readline().decode("utf-8").strip()
                    if line:
                        _LOGGER.debug(f"Received data: {line}")
                        try:
                            count = int(line)
                            with self._lock:
                                self.people_count = count
                        except ValueError:
                            _LOGGER.error(f"Received non-integer data: {line}")
                except serial.SerialException as e:
                    _LOGGER.error(f"Serial exception: {e}")
                    self.data_connection.close()
                    self.connect_data()
                except Exception as e:
                    _LOGGER.error("Error reading radar data: %s", e)
            else:
                _LOGGER.warning("Data connection not open. Attempting to reconnect...")
                self.connect_data()
            time.sleep(0.1)

    def get_people_count(self):
        with self._lock:
            return self.people_count

    def stop(self):
        self._stop_event.set()
        if hasattr(self, 'read_thread') and self.read_thread.is_alive():
            self.read_thread.join()
        if self.cli_connection and self.cli_connection.is_open:
            self.cli_connection.close()
        if self.data_connection and self.data_connection.is_open:
            self.data_connection.close()
