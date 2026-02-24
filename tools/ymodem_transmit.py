import os
import serial
import time

SOH = b'\x01'  # 128-byte block
STX = b'\x02'  # 1024-byte block
EOT = b'\x04'
ACK = b'\x06'
NAK = b'\x15'
CAN = b'\x18'
CRC = b'C'

PACKET_SIZE = 1024
MAX_RETRIES = 10
TIMEOUT_FIRST = 15   # Timeout for first 'C'
TIMEOUT_RESPONSE = 10  # Timeout for normal responses

def send_packet(ser, pkt_type, pkt_num, data):
    if pkt_type == STX:
        size = 1024
    else:
        size = 128
    data = data.ljust(size, b'\x1A')
    pkt = pkt_type + bytes([pkt_num]) + bytes([255 - pkt_num]) + data
    crc = crc16(data)
    pkt += bytes([(crc >> 8) & 0xFF, crc & 0xFF])
    ser.write(pkt)

def crc16(data):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def send_file(ser, filepath):
    filename = os.path.basename(filepath).encode()
    filesize = os.path.getsize(filepath)
    print(f"Sending: {filename.decode()} ({filesize} bytes)")

    # Step 1: Wait for receiver to send 'C'
    print("Waiting for receiver...")
    ser.timeout = TIMEOUT_FIRST
    try:
        while True:
            char = ser.read(1)
            if char == CRC:
                print("[INFO] Receiver ready.")
                break
    except serial.SerialTimeoutException:
        print("[ERROR] Timeout waiting for initial 'C'")
        return False

    # Step 2: Send header packet
    header = filename + b'\x00' + str(filesize).encode() + b'\x00'
    send_packet(ser, SOH, 0, header)
    ser.timeout = TIMEOUT_RESPONSE
    if ser.read(1) != ACK:
        print("[ERROR] ACK not received for header")
        return False
    if ser.read(1) != CRC:
        print("[ERROR] CRC not received after header")
        return False

    # Step 3: Send file in 1K packets
    pkt_num = 1
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(PACKET_SIZE)
            if not data:
                break
            for attempt in range(MAX_RETRIES):
                send_packet(ser, STX, pkt_num % 256, data)
                resp = ser.read(1)
                if resp == ACK:
                    break
                else:
                    print(f"[WARN] No ACK for block {pkt_num}, retrying...")
            else:
                print("[ERROR] Failed to send block after retries.")
                return False
            pkt_num += 1

    # Step 4: Send EOT until ACK
    for _ in range(MAX_RETRIES):
        print("Sending EOT")
        ser.write(EOT)
        resp = ser.read(1)
        if resp == ACK:
            print("[INFO] EOT acknowledged.")
            break
        else:
            print("[WARN] EOT not acknowledged, retrying...")
            time.sleep(1)
    else:
        print("[ERROR] EOT not acknowledged after retries.")
        return False

    # Step 5: Final empty header
    send_packet(ser, SOH, 0, b'\x00')
    if ser.read(1) != ACK:
        print("[ERROR] Final empty header not acknowledged.")
        return False

    print("✅ File transfer complete.")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YMODEM Sender")
    parser.add_argument("port", help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument("file", help="File to send")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    args = parser.parse_args()

    try:
        with serial.Serial(args.port, args.baud, timeout=1) as ser:
            result = send_file(ser, args.file)
            if not result:
                print("[FAILED]")
    except serial.SerialException as e:
        print(f"[ERROR] Serial exception: {e}")