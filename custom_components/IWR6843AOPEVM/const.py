import logging

DOMAIN = "radar_integration"
DEFAULT_CLI_DEVICE_PATH = "/dev/serial/by-id/usb-Silicon_Labs_CP2105_Dual_USB_to_UART_Bridge_Controller_01083315-if00-port0"
DEFAULT_DATA_DEVICE_PATH = "/dev/serial/by-id/usb-Silicon_Labs_CP2105_Dual_USB_to_UART_Bridge_Controller_01083315-if01-port0"
LOGGER = logging.getLogger(__name__)
