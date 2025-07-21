import serial
import time
from PIL import Image

class VKP80IIIPrinter:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def open(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def write(self, data):
        self.ser.write(data)

    def reset(self):
        self.write(b'\x1B\x40')  # ESC @

    def set_encoding_latin1(self):
        # ESC t 0x10 -> Latin1 (ISO 8859-1)
        self.write(bytes([0x1B, 0x74, 0x10]))

    def set_align(self, mode):
        modes = {'left': 0, 'center': 1, 'right': 2}
        self.write(bytes([0x1B, 0x61, modes.get(mode, 1)]))

    def feed_lines(self, n):
        self.write(bytes([0x1B, 0x64, n]))

    def set_font_size(self, width=1, height=1):
        value = ((height - 1) << 4) | (width - 1)
        self.write(bytes([0x1D, 0x21, value]))

    def cut_paper(self, mode='eject', length=6, blink=True, timeout=1):
        """
        Ejecuta corte y entrega/retractado en modo presentaciÃ³n.

        Args:
            length (int): Longitud visible en mm (por ej. 6 u 8 mm).
            mode (str): 'eject' o 'retract' para entregar o retraer si no se recoge.
            blink (bool): Si parpadea el LED.
            timeout (int): Tiempo en segundos antes de retraer si no se recoge.
        """

        a = length
        b = 0x01 if blink else 0x00
        c = 0x45 if mode == 'eject' else 0x52
        d = max(1, min(timeout, 255))

        self.write(bytes([0x1C, 0x50, a, b, c, d]))

    def present_ticket(self, mm=87):
        self.write(bytes([0x1D, 0x65, 0x05]))          # GS e 05 - eject
        self.write(bytes([0x1B, 0x69]))                # ESC i - total cut
        self.write(bytes([0x1D, 0x65, 0x03, mm]))      # GS e 03 mm - present N mm

    def print_text(self, text):
        self.write(text.encode('latin1', errors='replace'))
        self.write(b'\n')

    def print_image(self, path, invert=False):
        img = Image.open(path).convert('1')
        width, height = img.size
        width_bytes = (width + 7) // 8

        data = bytearray()
        data += b'\x1D\x76\x30\x00'
        data += bytes([width_bytes % 256, width_bytes // 256])
        data += bytes([height % 256, height // 256])

        pixels = img.tobytes()
        
        if invert:
            # Invertir cada byte
            pixels = bytes([~b & 0xFF for b in pixels])

        data += pixels

        self.write(data)

    def print_qr(self, data, module_size=4):
        if not (1 <= module_size <= 16):
            raise ValueError("module_size debe estar entre 1 y 16")

        # Select QR model (model 2)
        self.write(b'\x1D\x28\x6B\x04\x00\x31\x41\x32\x00')
        
        # Set module size (1 to 16)
        self.write(bytes([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x43, module_size]))

        # Set error correction level (48 = L, 49 = M, 50 = Q, 51 = H)
        self.write(b'\x1D\x28\x6B\x03\x00\x31\x45\x31')

        # Store data
        length = len(data) + 3
        pL = length % 256
        pH = length // 256
        self.write(bytes([0x1D, 0x28, 0x6B, pL, pH, 0x31, 0x50, 0x30]) + data.encode('latin1'))

        # Print QR code
        self.write(b'\x1D\x28\x6B\x03\x00\x31\x51\x30')