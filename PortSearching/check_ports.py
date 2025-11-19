# check_ports.py
import serial.tools.list_ports

print("Mevcut seri portlar listeleniyor:")
ports = serial.tools.list_ports.comports()

if not ports:
    print("Hiç seri port bulunamadı.")
else:
    for port in ports:
        print(f"  Cihaz: {port.device}")
        print(f"  Açıklama: {port.description}")
        print(f"  HWID: {port.hwid}")
        print("-" * 20)