import serial
import serial.tools.list_ports
import time

def find_stm32_port():
    """
    Auto-detects STM32 Blackpill port by listing all /dev/ttyUSB* or /dev/ttyACM* devices.
    Returns the first available port.
    """
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "USB" in p.device or "ACM" in p.device:
            print(f"Found port: {p.device}")
            return p.device
    return None

# Detect STM32 port
port = find_stm32_port()
if port is None:
    print("No STM32 or USB-TTL device found!")
    exit(1)

# Open serial connection
baudrate = 115200
ser = serial.Serial(port, baudrate)
time.sleep(2)  # Wait for STM32 reset

print(f"Connected to STM32 on {port} at {baudrate} baud.")

# Send messages every 500 ms
try:
    while True:
        message = "Hello from Python!\n"
        ser.write(message.encode())
        print(f"Sent: {message.strip()}")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()

