import serial
import struct
import logging

_LOGGER = logging.getLogger(__name__)

# Constants
MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST = 1010

# Pre-compiled Structs for efficiency
HEADER_STRUCT = struct.Struct('Q8I')       # Header: 1 unsigned long long, 8 unsigned ints
TLV_HEADER_STRUCT = struct.Struct('II')    # TLV Header: 2 unsigned ints
TARGET_STRUCT = struct.Struct('I27f')      # Target: 1 unsigned int, 27 floats

HEADER_LEN = HEADER_STRUCT.size
TLV_HEADER_LEN = TLV_HEADER_STRUCT.size
TARGET_SIZE = TARGET_STRUCT.size

# Magic word as bytes for faster comparison
UART_MAGIC_WORD = b'\x02\x01\x04\x03\x06\x05\x08\x07'
MAGIC_WORD_LEN = len(UART_MAGIC_WORD)

def parseStandardFrame(frameData):
    """Parses a standard frame and returns the people count or -1 on error."""
    try:
        header = HEADER_STRUCT.unpack(frameData[:HEADER_LEN])
        frameData = frameData[HEADER_LEN:]
        numTLVs = header[7]
        for _ in range(numTLVs):
            tlvType, tlvLength = TLV_HEADER_STRUCT.unpack(frameData[:TLV_HEADER_LEN])
            frameData = frameData[TLV_HEADER_LEN:]
            if tlvType == MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST:
                numDetectedTargets = tlvLength // TARGET_SIZE
                return numDetectedTargets if numDetectedTargets > 0 else 0
            frameData = frameData[tlvLength:]
    except struct.error:
        _LOGGER.error("Error parsing frame.")
    return -1

class RadarReader:
    def __init__(self, data_device_path):
        self.data_device_path = data_device_path
        self.serial_connection = None
        self.connect()

    def connect(self):
        if self.serial_connection and self.serial_connection.is_open:
            return
        try:
            self.serial_connection = serial.Serial(
                port=self.data_device_path,
                baudrate=921600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.6
            )
            self.serial_connection.reset_output_buffer()
            _LOGGER.info(f"Connected to radar at {self.data_device_path}")
        except serial.SerialException as e:
            _LOGGER.error(f"Failed to connect to radar: {e}")
            self.serial_connection = None

    def get_people_count(self):
        if not self.serial_connection or not self.serial_connection.is_open:
            self.connect()
        if self.serial_connection:
            try:
                buffer = self.serial_connection.read(1024)
                if not buffer:
                    _LOGGER.error("ERROR: No data detected on Data port, read timed out")
                    return 0
                magic_index = buffer.find(UART_MAGIC_WORD)
                if magic_index == -1:
                    _LOGGER.error("Magic word not found in data stream.")
                    return 0
                frameData = bytearray(buffer[magic_index:])
                while len(frameData) < MAGIC_WORD_LEN + 8:
                    to_read = 8 - (len(frameData) - MAGIC_WORD_LEN)
                    more_data = self.serial_connection.read(to_read)
                    if not more_data:
                        _LOGGER.error("ERROR: Incomplete header received.")
                        return 0
                    frameData += more_data
                version, length = struct.unpack('<II', frameData[MAGIC_WORD_LEN:MAGIC_WORD_LEN + 8])
                remaining_length = length - (MAGIC_WORD_LEN + 8)
                if remaining_length < 0:
                    _LOGGER.error("ERROR: Invalid frame length.")
                    return 0
                while len(frameData) < length:
                    to_read = length - len(frameData)
                    more_data = self.serial_connection.read(to_read)
                    if not more_data:
                        _LOGGER.error("ERROR: Incomplete frame received.")
                        return 0
                    frameData += more_data
                return parseStandardFrame(frameData)
            except serial.SerialException as e:
                _LOGGER.error(f"Serial communication error: {e}")
                return 0
            except Exception as e:
                _LOGGER.error(f"Unexpected error: {e}")
                return 0
        return 0