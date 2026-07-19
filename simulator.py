# simulator.py
# Bu betik, roketin telemetri verisini simüle eder.
# Binary protokol formatında (78 byte) veri gönderir.
# main.c'deki paketle_gonder() yeni paket formatına göre güncellenmiştir.

import serial
import time
import random
import struct
import math
from src.core import config

paket_sayac = 0   # Simülasyon için sayaç (sınırsız artar)
packet_counter = 0  # Paket sayacı (0-255 döngüsel)

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

# Durum ve Kontrol
durum = 0  # 0: Beklemede, 1: Yükseliyor, 2: Tepe Noktası, 3: İniş

# Simülatör Konfigürasyonu
PORT = 'COM2'
BAUDRATE = config.RECEIVER_BAUDRATE

print(f"Roket Simülatörü Başlatıldı. {PORT} portuna {BAUDRATE} baud rate ile yazılıyor.")
print("Binary protokol formatında (78 byte) veri gönderiliyor.")
print("main.c yeni paket formatı kullanılıyor:")
print("  Byte 4  : Nem (%)")
print("  Byte 34 : GY BME280 Basınç (Pa)")
print("  Byte 38 : GY Sıcaklık (°C)")
print("Durdurmak için Ctrl+C.")


def create_binary_packet(nem_yuzde, counter, irtifa,
                         roket_gps_irtifa, roket_enlem, roket_boylam,
                         gorev_gps_irtifa, gorev_enlem, gorev_boylam,
                         gorev_basinc_pa, gorev_sicaklik_c,
                         jiroskop_x, jiroskop_y, jiroskop_z,
                         ivme_x, ivme_y, ivme_z, aci, durum):
    """
    78 byte uzunluğunda binary paket oluşturur.
    main.c paketle_gonder() fonksiyonunu birebir taklit eder.

    Paket yapısı:
    [0-3]   Header: FF FF 54 52
    [4]     Nem (%) - UINT8      (main.c L150: TAKIM ID yerine nem)
    [5]     Sayaç - UINT8
    [6-9]   İrtifa - Float32     (UKB[0-3])
    [10-13] Roket GPS İrtifa     (UKB[4-7])
    [14-17] Roket Enlem          (UKB[8-11])
    [18-21] Roket Boylam         (UKB[12-15])
    [22-25] GY GPS İrtifa        (Gorev[4-7])
    [26-29] GY GPS Enlem         (Gorev[8-11])
    [30-33] GY GPS Boylam        (Gorev[12-15])
    [34-37] GY BME280 Basınç(Pa) (Gorev[0-3]) - main.c L134-135
    [38-41] GY Sıcaklık (°C)    (Gorev[16-19]) - main.c L146-147
    [42-45] Kullanılmıyor (0.0) - main.c'de yazılmıyor
    [46-49] Jiroskop X           (UKB[16-19])
    [50-53] Jiroskop Y           (UKB[20-23])
    [54-57] Jiroskop Z           (UKB[24-27])
    [58-61] İvme X               (UKB[28-31])
    [62-65] İvme Y               (UKB[32-35])
    [66-69] İvme Z               (UKB[36-39])
    [70-73] Açı                  (UKB[40-43])
    [74]    Durum - UINT8
    [75]    Checksum (Byte 4-74 toplamının mod 256)
    [76-77] Footer: 0D 0A

    Returns:
        bytes: 78 byte uzunluğunda binary paket
    """
    packet = bytearray(78)

    # Header [0-3]
    packet[0] = 0xFF
    packet[1] = 0xFF
    packet[2] = 0x54
    packet[3] = 0x52

    # Nem [4] - Byte 4: TAKIM ID yerine nem yazılıyor (main.c L150)
    packet[4] = int(nem_yuzde) & 0xFF

    # Sayaç [5]
    packet[5] = counter & 0xFF

    # İrtifa [6-9]
    struct.pack_into('<f', packet, 6, float(irtifa))

    # Roket GPS İrtifa [10-13]
    struct.pack_into('<f', packet, 10, float(roket_gps_irtifa))
    # Roket Enlem [14-17]
    struct.pack_into('<f', packet, 14, float(roket_enlem))
    # Roket Boylam [18-21]
    struct.pack_into('<f', packet, 18, float(roket_boylam))

    # GY GPS İrtifa [22-25]
    struct.pack_into('<f', packet, 22, float(gorev_gps_irtifa))
    # GY GPS Enlem [26-29]
    struct.pack_into('<f', packet, 26, float(gorev_enlem))
    # GY GPS Boylam [30-33]
    struct.pack_into('<f', packet, 30, float(gorev_boylam))

    # GY BME280 Basınç (Pa) [34-37] - main.c L134-135: "kademe irtifaya yaziliyor"
    struct.pack_into('<f', packet, 34, float(gorev_basinc_pa))

    # GY Sıcaklık (°C) [38-41] - main.c L146-147: "kademe enleme yaziliyor"
    struct.pack_into('<f', packet, 38, float(gorev_sicaklik_c))

    # [42-45] Boş - main.c'de bu slota hiçbir şey yazılmıyor (sıfır kalır)

    # Jiroskop X [46-49]
    struct.pack_into('<f', packet, 46, float(jiroskop_x))
    # Jiroskop Y [50-53]
    struct.pack_into('<f', packet, 50, float(jiroskop_y))
    # Jiroskop Z [54-57]
    struct.pack_into('<f', packet, 54, float(jiroskop_z))

    # İvme X [58-61]
    struct.pack_into('<f', packet, 58, float(ivme_x))
    # İvme Y [62-65]
    struct.pack_into('<f', packet, 62, float(ivme_y))
    # İvme Z [66-69]
    struct.pack_into('<f', packet, 66, float(ivme_z))

    # Açı [70-73]
    struct.pack_into('<f', packet, 70, float(aci))

    # Durum [74]
    packet[74] = durum & 0xFF

    # Checksum [75] — Byte 4'ten 74'e (dahil) toplamın mod 256'sı
    checksum = sum(packet[4:75]) % 256
    packet[75] = checksum

    # Footer [76-77]
    packet[76] = 0x0D
    packet[77] = 0x0A

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

        # --- Uçuş Durumu Simülasyonu ---
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

        # Yere inince sıfırla
        if irtifa == 0 and durum == 3:
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
            nem, packet_counter,
            irtifa,
            roket_gps_irtifa, roket_enlem, roket_boylam,
            gorev_gps_irtifa, gorev_enlem, gorev_boylam,
            gorev_basinc, gorev_sicaklik,
            jiroskop_x, jiroskop_y, jiroskop_z,
            ivme_x, ivme_y, ivme_z,
            aci, durum
        )

        ser.write(binary_packet)

        checksum = binary_packet[75]
        print(f"Gönderildi: #{packet_counter} (Sim:{paket_sayac}) | İrtifa: {irtifa:.1f}m | "
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
