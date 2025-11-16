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
temperature = 20.0
pressure = 1013.25
battery = 12.6

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
        temperature = random.uniform(15.0, 30.0)
        pressure = random.uniform(1000.0, 1020.0)
        battery -= random.uniform(0.001, 0.005)  # Batarya azalır

        # Her veri tipini ayrı satırda gönder
        data_list = [
            f"LAT,{latitude:.6f}",
            f"LON,{longitude:.6f}",
            f"ALT,{altitude:.2f}",
            f"VEL,{velocity:.2f}",
            f"TEMP,{temperature:.1f}",
            f"PRES,{pressure:.2f}",
            f"BAT,{battery:.2f}"
        ]
        
        for data in data_list:
            ser.write(f"{data}\n".encode('utf-8'))
            print(f"Gönderildi: {data}")
        
        print("---")

        # 10Hz (saniyede 10 kez) veri göndermek için 0.1 saniye bekle
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nSimülatör durduruldu.")
finally:
    if ser.is_open:
        ser.close()
        print(f"Port {ROCKET_PORT} kapatıldı.")