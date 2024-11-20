# SerialLoggerHandler

SerialLoggerHandler is a Python module designed to manage serial communication with Arduino devices. It simplifies tasks like detecting ports, parsing data, and handling connections.

## Features
- Automatically detect Arduino serial ports.
- Easy-to-use interface for connecting, disconnecting, and streaming data.
- Callback-based architecture for processing incoming serial data.

## Installation
You can install this module locally using pip:

```bash
pip install .
```

Or directly from GitHub:

```bash
pip install git+https://github.com/yourusername/SerialLoggerHandler.git
```

## Usage
Here’s an example of how to use SerialLoggerHandler:

```python
from SerialLoggerHandler import SerialLoggerHandler

def handle_data(data):
    print("Received data:", data)

logger = SerialLoggerHandler()
logger.setPort("/dev/ttyUSB0")
logger.setBaudRate(115200)
logger.setCallback(handle_data)
logger.start()

# Stop when done
logger.stop()
```

## License
MIT License