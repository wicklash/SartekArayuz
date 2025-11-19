# simulator.py
# Bu betik, roketin telemetri verisini simüle eder.
# COM7 portuna veri yazar.

import serial
import time
import random
import struct

# ROKET PORTU: com0com ile oluşturduğunuz çiftin BİRİNCİ ucu
ROCKET_PORT = 'COM7' 
BAUDRATE = 9600

# Takım bilgileri
TAKIM_ID = 123456  # Takım numarası
paket_sayac = 0

# Barometrik veri
irtifa = 0.0

# GPS Verileri - Ana Roket
roket_gps_irtifa = 0.0
roket_enlem = 39.9334  # Ankara örnek koordinatlar
roket_boylam = 32.8597

# GPS Verileri - Görev Yükü
gorev_gps_irtifa = 0.0
gorev_enlem = 39.9334
gorev_boylam = 32.8597

# GPS Verileri - Kademe
kademe_gps_irtifa = 0.0
kademe_enlem = 39.9334
kademe_boylam = 32.8597

# IMU Verileri
jiroskop_x = 0.0
jiroskop_y = 0.0
jiroskop_z = 0.0
ivme_x = 0.0
ivme_y = 0.0
ivme_z = 0.0
aci = 0.0

# Durum ve Kontrol
durum = 0  # 0: Beklemede, 1: Yükseliyor, 2: Tepe Noktası, 3: İniş

print(f"Roket Simülatörü Başlatıldı. {ROCKET_PORT} portuna {BAUDRATE} baud rate ile yazılıyor.")
print("Durdurmak için Ctrl+C.")

def calculate_crc(data_string):
    """Basit CRC-8 hesaplama"""
    crc = 0
    for byte in data_string.encode('utf-8'):
        crc ^= byte
    return crc

try:
    # Seriyal portu aç
    ser = serial.Serial(ROCKET_PORT, BAUDRATE, timeout=1)
except serial.SerialException as e:
    print(f"Hata: Port açılamadı ({ROCKET_PORT}). {e}")
    print("com0com çalışıyor mu? Doğru portu seçtiniz mi?")
    exit()

try:
    while True:
        # Paket sayacını artır
        paket_sayac += 1
        
        # Duruma göre simülasyon
        if paket_sayac < 50:
            durum = 0  # Beklemede
            irtifa += random.uniform(0, 0.5)
        elif paket_sayac < 200:
            durum = 1  # Yükseliyor
            irtifa += random.uniform(10.0, 20.0)
            ivme_z = random.uniform(15.0, 25.0)
        elif paket_sayac < 220:
            durum = 2  # Tepe noktası
            irtifa += random.uniform(-2.0, 2.0)
            ivme_z = random.uniform(-2.0, 2.0)
        else:
            durum = 3  # İniş
            irtifa -= random.uniform(5.0, 10.0)
            ivme_z = random.uniform(-5.0, -2.0)
        
        if irtifa < 0:
            irtifa = 0
        
        # GPS verileri (irtifa ile senkron)
        roket_gps_irtifa = irtifa + random.uniform(-2.0, 2.0)
        roket_enlem += random.uniform(-0.0001, 0.0001)
        roket_boylam += random.uniform(-0.0001, 0.0001)
        
        # Görev yükü ayrıldıysa farklı konumda
        if durum >= 2:
            gorev_gps_irtifa = irtifa * 0.8 + random.uniform(-5.0, 5.0)
            gorev_enlem = roket_enlem + random.uniform(-0.001, 0.001)
            gorev_boylam = roket_boylam + random.uniform(-0.001, 0.001)
        else:
            gorev_gps_irtifa = roket_gps_irtifa
            gorev_enlem = roket_enlem
            gorev_boylam = roket_boylam
        
        # Kademe ayrıldıysa farklı konumda
        if durum >= 2:
            kademe_gps_irtifa = irtifa * 0.6 + random.uniform(-10.0, 10.0)
            kademe_enlem = roket_enlem + random.uniform(-0.002, 0.002)
            kademe_boylam = roket_boylam + random.uniform(-0.002, 0.002)
        else:
            kademe_gps_irtifa = roket_gps_irtifa
            kademe_enlem = roket_enlem
            kademe_boylam = roket_boylam
        
        # IMU verileri
        jiroskop_x = random.uniform(-5.0, 5.0)
        jiroskop_y = random.uniform(-5.0, 5.0)
        jiroskop_z = random.uniform(-10.0, 10.0)
        ivme_x = random.uniform(-2.0, 2.0)
        ivme_y = random.uniform(-2.0, 2.0)
        aci = random.uniform(-5.0, 5.0)
        
        # Veri paketini oluştur (CSV formatında)
        data_parts = [
            str(TAKIM_ID),
            str(paket_sayac),
            f"{irtifa:.2f}",
            f"{roket_gps_irtifa:.2f}",
            f"{roket_enlem:.6f}",
            f"{roket_boylam:.6f}",
            f"{gorev_gps_irtifa:.2f}",
            f"{gorev_enlem:.6f}",
            f"{gorev_boylam:.6f}",
            f"{kademe_gps_irtifa:.2f}",
            f"{kademe_enlem:.6f}",
            f"{kademe_boylam:.6f}",
            f"{jiroskop_x:.2f}",
            f"{jiroskop_y:.2f}",
            f"{jiroskop_z:.2f}",
            f"{ivme_x:.2f}",
            f"{ivme_y:.2f}",
            f"{ivme_z:.2f}",
            f"{aci:.2f}",
            str(durum)
        ]
        
        data_string = ",".join(data_parts)
        
        # CRC hesapla ve ekle
        crc = calculate_crc(data_string)
        data_string += f",{crc}"
        
        # Veriyi gönder
        ser.write(f"{data_string}\n".encode('utf-8'))
        print(f"Gönderildi: Paket #{paket_sayac} | İrtifa: {irtifa:.2f}m | Durum: {durum} | CRC: {crc}")

        # 10Hz (saniyede 10 kez) veri göndermek için 0.1 saniye bekle
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nSimülatör durduruldu.")
finally:
    if ser.is_open:
        ser.close()
        print(f"Port {ROCKET_PORT} kapatıldı.")