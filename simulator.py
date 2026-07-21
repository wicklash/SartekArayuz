# simulator.py
# Bu betik, roketin telemetri verisini simüle eder.
# Binary protokol formatında (75 byte) veri gönderir.
# Yeni paket formatına göre güncellenmiştir (2026-07-21).

import serial
import time
import random
import struct
import math
from src.core import config

paket_sayac = 0   # Simülasyon için sayaç (sınırsız artar)
packet_counter = 0   # UKB paket sayaçı (0-255 döngüsel)
gorev_packet_counter = 0  # Görev yükü paket sayaçı (0-255 döngüsel)

# Barometrik veri (Roket Ana Kart - UKB)
irtifa = 0.0

# GPS Verileri - Ana Roket
roket_gps_irtifa = 0.0
roket_enlem = 39.9334  # Ankara örnek koordinatlar
roket_boylam = 32.8597

# GPS Verileri - Görev Yükü
gorev_gps_irtifa = 0.0
gorev_enlem = 39.9334
gorev_boylam = 32.8597

# IMU Verileri
jiroskop_x = 0.0
jiroskop_y = 0.0
jiroskop_z = 0.0
ivme_x = 0.0
ivme_y = 0.0
ivme_z = 0.0
aci = 0.0

# Görev Yükü Ortam Verileri (BME280)
gorev_basinc    = 101325.0   # Pa cinsinden (deniz seviyesi ~101325 Pa)
gorev_sicaklik  = 25.0       # °C cinsinden
nem             = 50         # % cinsinden (uint8, Byte 4)

# Durum ve Kontrol (roket_durum_t: 0:Uçuşa Hazırlık, 1:Uçuş, 2:Apogee, 3:1.Ayrılma, 4:2.Ayrılma, 5:İniş)
durum = 0

# Simülatör Konfigürasyonu
PORT = 'COM2'
BAUDRATE = config.RECEIVER_BAUDRATE

print(f"Roket Simülasörü Başlatıldı. {PORT} portuna {BAUDRATE} baud rate ile yazılıyor.")
print("Binary protokol formatında (75 byte) veri gönderiliyor.")
print("Yeni paket formatı (2026-07-21):")
print("  Byte 0-3  : Header (FF FF 54 52)")
print("  Byte 4-47 : UKB Verileri (İrtifa, GPS, IMU, Açı)")
print("  Byte 48   : Roket Durum")
print("  Byte 49   : UKB Sayaçı")
print("  Byte 50-69: Görev Yükü Verileri (Basınç, GPS, Sıcaklık)")
print("  Byte 70   : GY Nem")
print("  Byte 71   : GY Sayaçı")
print("  Byte 72   : Checksum")
print("  Byte 73-74: Footer (0D 0A)")
print("Durdurmak için Ctrl+C.")


def create_binary_packet(ukb_sayac, gorev_sayac, irtifa,
                         roket_gps_irtifa, roket_enlem, roket_boylam,
                         jiroskop_x, jiroskop_y, jiroskop_z,
                         ivme_x, ivme_y, ivme_z, aci, durum,
                         gorev_basinc_pa, gorev_gps_irtifa,
                         gorev_enlem, gorev_boylam, gorev_sicaklik_c,
                         nem_yuzde):
    """
    75 byte uzunluğunda binary paket oluşturur.
    Yeni paket formatına göre (2026-07-21).

    Paket yapısı:
    [0-3]   Header: FF FF 54 52
    [4-7]   Roket İrtifa      - float32
    [8-11]  Roket GPS İrtifa  - float32
    [12-15] Roket Enlem        - float32
    [16-19] Roket Boylam       - float32
    [20-23] Jiroskop X         - float32
    [24-27] Jiroskop Y         - float32
    [28-31] Jiroskop Z         - float32
    [32-35] İvme X             - float32
    [36-39] İvme Y             - float32
    [40-43] İvme Z             - float32
    [44-47] Roket Açı          - float32
    [48]    Roket Durum        - uint8
    [49]    UKB Sayaçı         - uint8
    [50-53] GY Basınç (Pa)    - float32
    [54-57] GY GPS İrtifa      - float32
    [58-61] GY Enlem           - float32
    [62-65] GY Boylam          - float32
    [66-69] GY Sıcaklık (°C)  - float32
    [70]    GY Nem (%)         - uint8
    [71]    GY Sayaçı          - uint8
    [72]    Checksum           - uint8  (sum(byte[4..71]) % 256)
    [73-74] Footer: 0D 0A

    Returns:
        bytes: 75 byte uzunluğunda binary paket
    """
    packet = bytearray(75)

    # Header [0-3]
    packet[0] = 0xFF
    packet[1] = 0xFF
    packet[2] = 0x54
    packet[3] = 0x52

    # --- UKB Verileri ---

    # Roket İrtifa [4-7]
    struct.pack_into('<f', packet, 4, float(irtifa))

    # Roket GPS İrtifa [8-11]
    struct.pack_into('<f', packet, 8, float(roket_gps_irtifa))

    # Roket Enlem [12-15]
    struct.pack_into('<f', packet, 12, float(roket_enlem))

    # Roket Boylam [16-19]
    struct.pack_into('<f', packet, 16, float(roket_boylam))

    # Jiroskop X [20-23]
    struct.pack_into('<f', packet, 20, float(jiroskop_x))

    # Jiroskop Y [24-27]
    struct.pack_into('<f', packet, 24, float(jiroskop_y))

    # Jiroskop Z [28-31]
    struct.pack_into('<f', packet, 28, float(jiroskop_z))

    # İvme X [32-35]
    struct.pack_into('<f', packet, 32, float(ivme_x))

    # İvme Y [36-39]
    struct.pack_into('<f', packet, 36, float(ivme_y))

    # İvme Z [40-43]
    struct.pack_into('<f', packet, 40, float(ivme_z))

    # Roket Açı [44-47]
    struct.pack_into('<f', packet, 44, float(aci))

    # Roket Durum [48]
    packet[48] = durum & 0xFF

    # UKB Sayaçı [49]
    packet[49] = ukb_sayac & 0xFF

    # --- Görev Yükü Verileri ---

    # GY Basınç (Pa) [50-53]
    struct.pack_into('<f', packet, 50, float(gorev_basinc_pa))

    # GY GPS İrtifa [54-57]
    struct.pack_into('<f', packet, 54, float(gorev_gps_irtifa))

    # GY Enlem [58-61]
    struct.pack_into('<f', packet, 58, float(gorev_enlem))

    # GY Boylam [62-65]
    struct.pack_into('<f', packet, 62, float(gorev_boylam))

    # GY Sıcaklık (°C) [66-69]
    struct.pack_into('<f', packet, 66, float(gorev_sicaklik_c))

    # GY Nem (%) [70]
    packet[70] = int(nem_yuzde) & 0xFF

    # GY Sayaçı [71]
    packet[71] = gorev_sayac & 0xFF

    # Checksum [72] — sum(byte[4..71]) % 256
    checksum = sum(packet[4:72]) % 256
    packet[72] = checksum

    # Footer [73-74]
    packet[73] = 0x0D
    packet[74] = 0x0A

    return bytes(packet)


try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
except serial.SerialException as e:
    print(f"Hata: Port açılamadı ({PORT}). {e}")
    print("com0com çalışıyor mu? Doğru portu seçtiniz mi?")
    input("\nKapatmak için Enter tuşuna basın...")
    exit()

try:
    while True:
        paket_sayac += 1
        packet_counter = (packet_counter + 1) % 256
        gorev_packet_counter = (gorev_packet_counter + 1) % 256
        # --- Uçuş Durumu Simülasyonu (roket_durum_t) ---
        if paket_sayac < 40:
            durum = 0  # 0: DURUM_UCUSA_HAZIRLIK
            irtifa += random.uniform(0, 0.2)
        elif paket_sayac < 160:
            durum = 1  # 1: DURUM_UCUS
            irtifa += random.uniform(15.0, 25.0)
            ivme_z = random.uniform(15.0, 25.0)
        elif paket_sayac < 180:
            durum = 2  # 2: DURUM_APOGEE
            irtifa += random.uniform(-1.0, 1.0)
            ivme_z = random.uniform(-1.0, 1.0)
        elif paket_sayac < 200:
            durum = 3  # 3: DURUM_BIRINCI_AYRILMA
            irtifa -= random.uniform(5.0, 10.0)
            ivme_z = random.uniform(-3.0, -1.0)
        elif paket_sayac < 220:
            durum = 4  # 4: DURUM_IKINCI_AYRILMA
            irtifa -= random.uniform(8.0, 12.0)
            ivme_z = random.uniform(-4.0, -2.0)
        else:
            durum = 5  # 5: DURUM_INIS
            irtifa -= random.uniform(10.0, 15.0)
            ivme_z = random.uniform(-5.0, -2.0)

        if irtifa < 0:
            irtifa = 0

        # Yere inince (İniş durumundayken irtifa 0 olunca) sıfırla
        if irtifa == 0 and durum == 5:
            print("--- Roket yere indi, simülasyon 2 saniye içinde yeniden başlayacak ---")
            time.sleep(2)
            paket_sayac = 0
            irtifa = 0.0
            roket_enlem = 39.9334
            roket_boylam = 32.8597
            gorev_enlem = 39.9334
            gorev_boylam = 32.8597
            print("--- Simülasyon yeniden başlatıldı ---")

        # GPS (irtifa ile senkron)
        roket_gps_irtifa = irtifa + random.uniform(-2.0, 2.0)
        roket_enlem += random.uniform(-0.0001, 0.0001)
        roket_boylam += random.uniform(-0.0001, 0.0001)

        if durum >= 2:
            gorev_gps_irtifa = irtifa * 0.8 + random.uniform(-5.0, 5.0)
            gorev_enlem = roket_enlem + random.uniform(-0.001, 0.001)
            gorev_boylam = roket_boylam + random.uniform(-0.001, 0.001)
        else:
            gorev_gps_irtifa = roket_gps_irtifa
            gorev_enlem = roket_enlem
            gorev_boylam = roket_boylam

        # IMU
        jiroskop_x = random.uniform(-5.0, 5.0)
        jiroskop_y = random.uniform(-5.0, 5.0)
        jiroskop_z = random.uniform(-10.0, 10.0)
        ivme_x = random.uniform(-2.0, 2.0)
        ivme_y = random.uniform(-2.0, 2.0)
        aci = random.uniform(-5.0, 5.0)

        # --- BME280 Ortam Simülasyonu ---
        # İrtifa arttıkça basınç düşer (gerçekçi atmosfer modeli)
        # P = P0 * (1 - L*h/T0)^(g*M/R*L) ≈ deniz seviyesi: 101325 Pa
        basinc_hpa_sim = 1013.25 * math.pow(1.0 - (0.0065 * irtifa / 288.15), 5.2561)
        gorev_basinc = basinc_hpa_sim * 100.0  # hPa -> Pa

        # Sıcaklık: irtifa arttıkça düşer (~6.5°C / 1000m)
        gorev_sicaklik = 25.0 - (irtifa * 0.0065) + random.uniform(-0.5, 0.5)

        # Nem: 40-80% arası rastgele (uint8)
        nem = int(random.uniform(40, 80))

        # Binary paket oluştur
        binary_packet = create_binary_packet(
            packet_counter, gorev_packet_counter,
            irtifa,
            roket_gps_irtifa, roket_enlem, roket_boylam,
            jiroskop_x, jiroskop_y, jiroskop_z,
            ivme_x, ivme_y, ivme_z,
            aci, durum,
            gorev_basinc, gorev_gps_irtifa,
            gorev_enlem, gorev_boylam, gorev_sicaklik,
            nem
        )

        ser.write(binary_packet)

        checksum = binary_packet[72]
        print(f"Gönderildi: UKB#{packet_counter} GY#{gorev_packet_counter} (Sim:{paket_sayac}) | İrtifa: {irtifa:.1f}m | "
              f"Basınç: {gorev_basinc:.0f}Pa | Sıcaklık: {gorev_sicaklik:.1f}°C | "
              f"Nem: %{nem} | Durum: {durum} | CS: {checksum}")

        time.sleep(1/15)  # ~15Hz

except KeyboardInterrupt:
    print("\nSimülatör durduruldu.")
except Exception as e:
    print(f"\nBeklenmeyen bir hata oluştu: {e}")
    input("\nKapatmak için Enter tuşuna basın...")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print(f"Port {PORT} kapatıldı.")
