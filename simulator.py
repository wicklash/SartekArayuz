# simulator.py
# Bu betik, roketin telemetri verisini simüle eder.
# COM5 portuna (veya Linux'ta /dev/pts/X) veri yazar.

import serial
import time
import random

# ROKET PORTU: com0com ile oluşturduğunuz çiftin BİRİNCİ ucu
ROCKET_PORT = 'COM7' 
BAUDRATE = 9600

# Sahte veri üretmek için başlangıç değerleri
altitude = 0.0
velocity = 0.0
latitude = 40.7128
longitude = -74.0060

print(f"Roket Simülatörü Başlatıldı. {ROCKET_PORT} portuna {BAUDRATE} baud rate ile yazılıyor.")
print("Durdurmak için Ctrl+C.")

try:
    # Seriyal portu aç
    ser = serial.Serial(ROCKET_PORT, BAUDRATE, timeout=1)
except serial.SerialException as e:
    print(f"Hata: Port açılamadı ({ROCKET_PORT}). {e}")
    print("com0com veya socat çalışıyor mu? Doğru portu seçtiniz mi?")
    exit()

try:
    while True:
        # Veriyi güncelle
        altitude += random.uniform(5.0, 15.0)
        velocity = random.uniform(45.0, 55.0)
        latitude += random.uniform(-0.0001, 0.0001)
        longitude += random.uniform(-0.0001, 0.0001)

        # Veri paketini oluştur (Basit bir CSV formatı)
        # GCS tarafında bu formatı ayrıştırmamız gerekecek.
        # \n (newline) karakteri önemlidir, GCS'de 'readline' bunu kullanır.
        data_packet = f"DATA,{altitude:.2f},{velocity:.2f},{latitude:.6f},{longitude:.6f}\n"

        # Veriyi port'a yaz (byte olarak encode ederek)
        ser.write(data_packet.encode('utf-8'))
        
        print(f"Gönderildi: {data_packet.strip()}")

        # 10Hz (saniyede 10 kez) veri göndermek için 0.1 saniye bekle
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nSimülatör durduruldu.")
finally:
    if ser.is_open:
        ser.close()
        print(f"Port {ROCKET_PORT} kapatıldı.")