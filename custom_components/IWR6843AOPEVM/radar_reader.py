import serial
import struct
import logging
import time

# Constants
MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST = 1010

# Pre-compiled Structs for efficiency
HEADER_STRUCT = struct.Struct('Q8I')       # Header: 1 unsigned long long, 8 unsigned ints
TLV_HEADER_STRUCT = struct.Struct('II')    # TLV Header: 2 unsigned ints
TARGET_STRUCT = struct.Struct('I27f')      # Target: 1 unsigned int, 27 floats

HEADER_LEN = HEADER_STRUCT.size
TLV_HEADER_LEN = TLV_HEADER_STRUCT.size
TARGET_SIZE = TARGET_STRUCT.size

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

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
        log.error("Error parsing frame.")
    return -1

class UARTParser:
    def connectComPorts(self, dataCom):
        try:
            self.dataCom = serial.Serial(
                port=dataCom,
                baudrate=921600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.6
            )
            self.dataCom.reset_output_buffer()
            log.info(f"Connected to {dataCom} successfully.")
        except serial.SerialException as e:
            log.error(f"Failed to connect to {dataCom}: {e}")
            raise

    def readAndParseUartDoubleCOMPort(self):
        self.fail = 0
        try:
            buffer = self.dataCom.read(1024)
            if not buffer:
                log.error("ERROR: No data detected on COM Port, read timed out")
                log.error("\tEnsure the device is in the proper mode and that the configuration is valid.")
                return -1
            magic_index = buffer.find(UART_MAGIC_WORD)
            while magic_index == -1:
                more_data = self.dataCom.read(1024)
                if not more_data:
                    log.error("ERROR: No data detected on COM Port, read timed out")
                    log.error("\tEnsure the device is in the proper mode and that the configuration is valid.")
                    return -1
                buffer += more_data
                magic_index = buffer.find(UART_MAGIC_WORD)
            frameData = bytearray(buffer[magic_index:])
            while len(frameData) < MAGIC_WORD_LEN + 8:
                to_read = 8 - (len(frameData) - MAGIC_WORD_LEN)
                more_data = self.dataCom.read(to_read)
                if not more_data:
                    log.error("ERROR: Incomplete header received.")
                    return -1
                frameData += more_data
            version, length = struct.unpack('<II', frameData[MAGIC_WORD_LEN:MAGIC_WORD_LEN + 8])
            remaining_length = length - (MAGIC_WORD_LEN + 8)
            if remaining_length < 0:
                log.error("ERROR: Invalid frame length.")
                return -1
            while len(frameData) < length:
                to_read = length - len(frameData)
                more_data = self.dataCom.read(to_read)
                if not more_data:
                    log.error("ERROR: Incomplete frame received.")
                    return -1
                frameData += more_data
            return parseStandardFrame(frameData)
        except serial.SerialException as e:
            log.error(f"Serial communication error: {e}")
            return -1
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            return -1

class Core:
    def __init__(self):
        self.device = "xWR6843"
        self.demo = "DEMO_3D_PEOPLE_TRACKING"
        self.parser = UARTParser()
        self.frameTime = 0.0

    def connectCom(self, dataCom):
        try:
            self.parser.connectComPorts(dataCom)
        except Exception as e:
            log.error(f"Error connecting to COM ports: {e}")

    def parseData(self):
        try:
            if self.parser and self.parser.dataCom.is_open:
                return self.parser.readAndParseUartDoubleCOMPort()
            else:
                log.error("UART parser is not initialized or data COM port is not open.")
        except Exception as e:
            log.error(f"Error parsing data: {e}")

if __name__ == "__main__":
    core = Core()
    core.device = "xWR6843"
    core.demo = "DEMO_3D_PEOPLE_TRACKING"
    core.connectCom("/dev/ttyUSB1")  # Adjust to your device path
    while True:
        people = core.parseData()
        if people >= 0:
            log.info(f"Detected {people} people.")
        else:
            log.error("Failed to detect people.")
        time.sleep(0.1)
