import serial
import serial.tools.list_ports
import time
import platform
def find_pico_port():
    """Findet automatisch den COM-Port des Raspberry Pi Pico"""
    ports = serial.tools.list_ports.comports()

    print("Verfügbare COM-Ports:")
    for i, port in enumerate(ports):
        print(f"  {i + 1}. {port.device} - {port.description}")

    # Versuche Pico automatisch zu finden
    for port in ports:
        if "USB Serial" in port.description or "Pico" in port.description:
            return port.device

    # Falls nicht gefunden, ersten Port nehmen oder manuell eingeben
    if ports:
        return ports[0].device
    return None


def read_rfid_uid_usb(com_port=None, timeout=10):
    """
    Liest eine RFID-UID vom Raspberry Pi Pico aus

    Args:
        com_port: COM-Port (wird automatisch erkannt falls None)
        timeout: Timeout in Sekunden für das Warten auf eine UID

    Returns:
        str: Die ausgelesene UID oder None bei Timeout/Fehler
    """
    if com_port is None:
        com_port = find_pico_port()
        if com_port is None:
            return None

    try:
        ser = serial.Serial(com_port, 115200, timeout=1)
        start_time = time.time()

        while True:
            # Timeout prüfen
            if time.time() - start_time > timeout:
                return None

            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                # UID Format prüfen (XX:XX:XX:XX)
                if line and ':' in line:
                    return line[14:]

    except Exception as e:
        print(f"Fehler beim Lesen der UID: {e}")
        return None
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()


def read_rfid_uid_uart(uart_port="/dev/ttyS0", baudrate=9600, timeout=10):
    """
    Liest RFID-UID über UART auf Raspberry Pi

    Args:
        uart_port: UART-Port (/dev/serial0 oder /dev/ttyAMA0)
        baudrate: Baudrate (Standard: 115200)
        timeout: Timeout in Sekunden

    Returns:
        str: Die ausgelesene UID oder None bei Fehler
    """
    try:
        ser = serial.Serial(uart_port, baudrate, timeout=1)
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                return None

            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                if line and ':' in line:
                    return line[14:] if len(line) > 14 else line

    except Exception as e:
        print(f"UART Fehler: {e}")
        return None
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()


def read_rfid_uid(port=None, timeout=10):
    """Automatische Erkennung für Windows (USB) und Raspberry Pi (UART)"""

    if platform.system() == "Windows":
        print(platform.system())
        # Windows: USB/COM-Port
        return read_rfid_uid_usb(port, timeout)
    else:
        # Linux/Raspberry Pi: UART
        print(platform.system())
        uart_port = port or "/dev/serial0"
        return read_rfid_uid_uart(uart_port, timeout=timeout)

if __name__ == "__main__":
    uid = read_rfid_uid()
    srtp_uid = uid[4:]
    print(srtp_uid)
