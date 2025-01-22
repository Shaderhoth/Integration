import serial
import struct
import logging
import sys
import asyncio
import os
import aiofiles

MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST = 1010
HEADER_STRUCT = struct.Struct('Q8I')
TLV_HEADER_STRUCT = struct.Struct('II')
TARGET_STRUCT = struct.Struct('I27f')
HEADER_LEN = HEADER_STRUCT.size
TLV_HEADER_LEN = TLV_HEADER_STRUCT.size
TARGET_SIZE = TARGET_STRUCT.size
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
UART_MAGIC_WORD = b'\x02\x01\x04\x03\x06\x05\x08\x07'
MAGIC_WORD_LEN = len(UART_MAGIC_WORD)

def parseStandardFrame(frameData):
    try:
        header = HEADER_STRUCT.unpack(frameData[:HEADER_LEN])
        frameData = frameData[HEADER_LEN:]
        numTLVs = header[7]
        for _ in range(numTLVs):
            tlvType, tlvLength = TLV_HEADER_STRUCT.unpack(frameData[:TLV_HEADER_LEN])
            frameData = frameData[TLV_HEADER_LEN:]
            if tlvType == MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST:
                log.error(f"Detected {tlvLength // TARGET_SIZE} people. at 1010")
                numDetectedTargets = tlvLength // TARGET_SIZE
                return numDetectedTargets if numDetectedTargets > 0 else 0
            frameData = frameData[tlvLength:]
    except struct.error:
        log.error("Error parsing frame.")
    return -1

class UARTParser:
    def connectComPorts(self, cliCom, dataCom):
        try:
            self.cliCom = serial.Serial(
                port=cliCom,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.dataCom = serial.Serial(
                port=dataCom,
                baudrate=921600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.dataCom.reset_output_buffer()
            log.info('Connected to COM ports successfully.')
        except serial.SerialException as e:
            log.error(f"Failed to connect to COM ports: {e}")
            raise

    def readAndParseUartDoubleCOMPort(self):
        try:
            buffer = self.dataCom.read(1024)
            if not buffer:
                return -1
            magic_index = buffer.find(UART_MAGIC_WORD)
            while magic_index == -1:
                more_data = self.dataCom.read(1024)
                if not more_data:
                    return -1
                buffer += more_data
                magic_index = buffer.find(UART_MAGIC_WORD)
            frameData = bytearray(buffer[magic_index:])
            while len(frameData) < MAGIC_WORD_LEN + 8:
                to_read = 8 - (len(frameData) - MAGIC_WORD_LEN)
                more_data = self.dataCom.read(to_read)
                if not more_data:
                    return -1
                frameData += more_data
            version, length = struct.unpack('<II', frameData[MAGIC_WORD_LEN:MAGIC_WORD_LEN + 8])
            remaining_length = length - (MAGIC_WORD_LEN + 8)
            if remaining_length < 0:
                return -1
            while len(frameData) < length:
                to_read = length - len(frameData)
                more_data = self.dataCom.read(to_read)
                if not more_data:
                    return -1
                frameData += more_data
            return parseStandardFrame(frameData)
        except Exception as e:
            log.error(f"Error reading UART data: {e}")
            return -1

    async def sendCfg(self, cfg):
        cfg = [line.strip() + '\n' for line in cfg if line.strip() and not line.startswith('%')]
        for line in cfg:
            await asyncio.sleep(0.03)
            self.cliCom.write(line.encode())
            await asyncio.sleep(0.03)
            while self.cliCom.in_waiting:
                ack = self.cliCom.readline().decode('utf-8', 'ignore').strip()
                log.info(ack)
                if ack.lower() == "done":
                    break

class Core:
    def __init__(self):
        self.device = "xWR6843"
        self.demo = "DEMO_3D_PEOPLE_TRACKING"
        self.parser = UARTParser()
        self.cfg = []

    def connectCom(self, cliCom, dataCom):
        self.parser.connectComPorts(cliCom, dataCom)

    async def selectCfg(self, filename):
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, filename)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Configuration file '{full_path}' not found.")
        self.cfg = []
        async with aiofiles.open(full_path, "r") as cfg_file:
            async for line in cfg_file:
                self.cfg.append(line.strip())


    async def sendCfg(self):
        await self.parser.sendCfg(self.cfg)

    def parseData(self):
        people = self.parser.readAndParseUartDoubleCOMPort()
        if people >= 0:
            log.error(f"Detected {people} people.")
        else:
            log.error("Failed to detect people.")
        return people