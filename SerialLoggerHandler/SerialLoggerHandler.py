import serial
import threading
import logging
from serial.tools import list_ports

class SerialLoggerHandler:
    def __init__(self, port="/dev/ttyUSB0", baud_rate=115200, timeout=1, debug=False):
        """
        Initialize the SerialLoggerHandler with default configuration.
        :param port: Serial port (e.g., "/dev/ttyUSB0").
        :param baud_rate: Baud rate for the connection.
        :param timeout: Timeout for serial reads (default: 1 second).
        :param debug: Enable detailed debug logging.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection = None
        self.is_listening = False
        self.data_handler = None
        self.debug = debug

        # Configure logging
        log_level = logging.DEBUG if self.debug else logging.CRITICAL
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger("SerialLoggerHandler")

    def setPort(self, port):
        """Set the serial port."""
        self.port = port
        print(f"Serial port: {self.port}")

    def detectPort(self):
        """
        Attempt to automatically detect the serial port used by the Arduino.
        :return: The detected port name, or None if no suitable port is found.
        """
        import time

        print("Detecting Arduino serial port...")
        available_ports = list_ports.comports()
        for port in available_ports:
            port_name = port.device
            self.logger.debug(f"Testing port: {port_name}")
            try:
                with serial.Serial(port_name, self.baud_rate, timeout=self.timeout) as test_serial:
                    for _ in range(5):  # Try reading multiple lines
                        line = test_serial.readline().decode("utf-8", errors="ignore").strip()
                        self.logger.debug(f"Read line: {line}")
                        if "D;" in line:  # Look for the marker
                            print(f"Detected Arduino on port: {port_name}")
                            self.port = port_name
                            return port_name
                        time.sleep(0.1)  # Allow some delay for data to arrive
            except (serial.SerialException, OSError) as e:
                self.logger.debug(f"Could not open port {port_name}: {e}")
        print("No Arduino detected.")
        return None

    def setBaudRate(self, baud_rate):
        """Set the baud rate."""
        self.baud_rate = baud_rate
        print(f"Baud rate: {self.baud_rate}")

    def setCallback(self, callback):
        """Set the callback function to process data."""
        if not callable(callback):
            raise ValueError("Callback must be a callable function.")
        self.data_handler = callback

    def _default_parse_data_line(self, line):
        """
        Parse a single line of serial data into key-value pairs.
        Processes lines containing "D;" and ignores the rest.
        """
        parsed_data = {}
        start_index = line.find("D;")  # Locate the "D;" marker
        if start_index != -1:
            kv_pairs = line[start_index + 2:].strip().split(";")  # Strip prefix and split pairs
            for pair in kv_pairs:
                if ":" in pair:  # Ensure key-value format
                    key, value = pair.split(":", 1)
                    parsed_data[key] = value
        return parsed_data

    def _listen_for_serial_data(self):
        self.logger.debug(f"Listening on {self.port} at {self.baud_rate} baud.\n")  # Added spacing here
        try:
            with serial.Serial(self.port, self.baud_rate, timeout=self.timeout) as serial_conn:
                self.serial_connection = serial_conn
                while self.is_listening:
                    try:
                        line = serial_conn.readline().decode("utf-8", errors="ignore").strip()
                        self.logger.debug(f"Raw data received: {line or '<empty>'}")
                        if not line:
                            continue
                        parsed_data = self._default_parse_data_line(line)
                        if parsed_data:
                            if self.data_handler:
                                self.data_handler(parsed_data)
                            else:
                                self.logger.warning("No data handler is set.")
                    except Exception as e:
                        self.logger.error(f"Error processing line: {e}")
        except serial.SerialException as e:
            self.logger.error(f"Serial error: {e}. Is the port in use?")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.serial_connection = None
            print("Stopped listening.")


    def start(self):
        """Start listening for data."""
        if self.is_listening:
            print("SerialLoggerHandler is already running.")
            return

        if not self.data_handler:
            raise ValueError("No callback function set. Use setCallback to configure a data handler.")

        self.is_listening = True
        threading.Thread(target=self._listen_for_serial_data, daemon=True).start()
        self.logger.debug("SerialLoggerHandler started.")

    def stop(self):
        """Stop listening for serial data."""
        if not self.is_listening:
            print("SerialLoggerHandler is not running.")
            return

        self.is_listening = False
        if self.serial_connection:
            self.serial_connection.close()
        self.logger.debug("SerialLoggerHandler has stopped.")
