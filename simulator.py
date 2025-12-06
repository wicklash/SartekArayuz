# simulator.py
# Bu betik, roketin telemetri verisini simüle eder.
# Binary protokol formatında (78 byte) veri gönderir.

import serial
import time
import random
import struct
from src.core.config import SERIAL_PORT_ROCKET, BAUDRATE, TEAM_ID

paket_sayac = 0  # Simülasyon için sayaç (sınırsız artar)
packet_counter = 0  # Paket sayacı (0-255 döngüsel)

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

print(f"Roket Simülatörü Başlatıldı. {SERIAL_PORT_ROCKET} portuna {BAUDRATE} baud rate ile yazılıyor.")
print("Binary protokol formatında (78 byte) veri gönderiliyor.")
print("Durdurmak için Ctrl+C.")


def create_binary_packet(team_id, counter, irtifa, roket_gps_irtifa, roket_enlem, roket_boylam,
                         gorev_gps_irtifa, gorev_enlem, gorev_boylam,
                         kademe_gps_irtifa, kademe_enlem, kademe_boylam,
                         jiroskop_x, jiroskop_y, jiroskop_z,
                         ivme_x, ivme_y, ivme_z, aci, durum):
    """
    78 byte uzunluğunda binary paket oluşturur.
    
    Protokol yapısı (EK-7):
    - Header (0-3): 0xFF, 0xFF, 0x54, 0x52
    - Takım ID (4): UINT8
    - Sayaç (5): UINT8 (0-255 döngüsel)
    - Payload (6-73): Float32 değerler (Little Endian)
    - Durum (74): UINT8
    - Checksum (75): Byte 4-74 arası toplamın mod 256
    - Footer (76-77): 0x0D, 0x0A
    
    Returns:
        bytes: 78 byte uzunluğunda binary paket
    """
    # 78 byte'lık paket oluştur
    packet = bytearray(78)
    
    # Header (Byte 0-3)
    packet[0] = 0xFF
    packet[1] = 0xFF
    packet[2] = 0x54
    packet[3] = 0x52
    
    # Takım ID (Byte 4)
    packet[4] = team_id & 0xFF  # UINT8
    
    # Sayaç (Byte 5) - 0-255 arası döngüsel
    packet[5] = counter & 0xFF  # UINT8
    
    # Payload (Byte 6-73): Float32 değerler (Little Endian <f)
    # Her float32 değeri 4 byte
    offset = 6
    
    # İrtifa
    struct.pack_into('<f', packet, offset, float(irtifa))
    offset += 4
    
    # Roket GPS
    struct.pack_into('<f', packet, offset, float(roket_gps_irtifa))
    offset += 4
    struct.pack_into('<f', packet, offset, float(roket_enlem))
    offset += 4
    struct.pack_into('<f', packet, offset, float(roket_boylam))
    offset += 4
    
    # Görev Yükü GPS
    struct.pack_into('<f', packet, offset, float(gorev_gps_irtifa))
    offset += 4
    struct.pack_into('<f', packet, offset, float(gorev_enlem))
    offset += 4
    struct.pack_into('<f', packet, offset, float(gorev_boylam))
    offset += 4
    
    # Kademe GPS
    struct.pack_into('<f', packet, offset, float(kademe_gps_irtifa))
    offset += 4
    struct.pack_into('<f', packet, offset, float(kademe_enlem))
    offset += 4
    struct.pack_into('<f', packet, offset, float(kademe_boylam))
    offset += 4
    
    # IMU - Jiroskop
    struct.pack_into('<f', packet, offset, float(jiroskop_x))
    offset += 4
    struct.pack_into('<f', packet, offset, float(jiroskop_y))
    offset += 4
    struct.pack_into('<f', packet, offset, float(jiroskop_z))
    offset += 4
    
    # IMU - İvme
    struct.pack_into('<f', packet, offset, float(ivme_x))
    offset += 4
    struct.pack_into('<f', packet, offset, float(ivme_y))
    offset += 4
    struct.pack_into('<f', packet, offset, float(ivme_z))
    offset += 4
    
    # Açı
    struct.pack_into('<f', packet, offset, float(aci))
    offset += 4
    
    # Durum (Byte 74)
    packet[74] = durum & 0xFF  # UINT8
    
    # Checksum (Byte 75): Byte 4 ile Byte 74 arasındaki tüm baytların toplamının mod 256'sı
    checksum = sum(packet[4:75]) % 256
    packet[75] = checksum
    
    # Footer (Byte 76-77)
    packet[76] = 0x0D
    packet[77] = 0x0A
    
    return bytes(packet)


try:
    # Seriyal portu aç
    ser = serial.Serial(SERIAL_PORT_ROCKET, BAUDRATE, timeout=1)
except serial.SerialException as e:
    print(f"Hata: Port açılamadı ({SERIAL_PORT_ROCKET}). {e}")
    print("com0com çalışıyor mu? Doğru portu seçtiniz mi?")
    exit()

try:
    while True:
        # Simülasyon sayacını artır
        paket_sayac += 1
        # Paket sayacını artır (0-255 arası döngüsel)
        packet_counter = (packet_counter + 1) % 256
        
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
        
        # Binary paket oluştur
        binary_packet = create_binary_packet(
            TEAM_ID, packet_counter,
            irtifa,
            roket_gps_irtifa, roket_enlem, roket_boylam,
            gorev_gps_irtifa, gorev_enlem, gorev_boylam,
            kademe_gps_irtifa, kademe_enlem, kademe_boylam,
            jiroskop_x, jiroskop_y, jiroskop_z,
            ivme_x, ivme_y, ivme_z,
            aci, durum
        )
        
        # Binary veriyi gönder
        ser.write(binary_packet)
        
        # Debug bilgisi
        checksum = binary_packet[75]
        print(f"Gönderildi: Paket #{packet_counter} (Sim: {paket_sayac}) | İrtifa: {irtifa:.2f}m | Durum: {durum} | Checksum: {checksum} | Boyut: {len(binary_packet)} byte")

        # 10Hz (saniyede 10 kez) veri göndermek için 0.1 saniye bekle
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nSimülatör durduruldu.")
finally:
    if ser.is_open:
        ser.close()
        print(f"Port {SERIAL_PORT_ROCKET} kapatıldı.")
