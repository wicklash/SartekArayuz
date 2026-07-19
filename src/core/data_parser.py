# data_parser.py
# Telemetri verisi parse mantığı
# Binary protokol formatını parse eder (78 byte)
# main.c'deki paketle_gonder() fonksiyonuna göre güncellenmiştir.

import struct
import math
from typing import Optional


class TelemetryData:
    """
    Telemetri veri modeli.
    main.c'deki yeni paket formatına göre güncellenmiştir:
    - Byte 4: Takım ID yerine Nem (uint8, %)
    - Byte 34-37: Kademe İrtifa yerine GY BME280 Basınç (float32, Pa)
    - Byte 38-41: Kademe Enlem yerine GY Sıcaklık (float32, °C)
    - Byte 42-45: Kullanılmıyor (0.0)
    - gorev_hesaplanan_irtifa: Basınç ve sıcaklıktan hesaplanan barometrik irtifa (m)
    Veriler saf sayı (float/int) olarak tutulur.
    Birim ekleme işi UI katmanında yapılır (performans için).
    """

    def __init__(self):
        # Sayaç
        self.sayac: int = 0

        # Nem (Byte 4 - Takım ID yerine)
        self.nem: int = 0

        # İrtifa (saf float) - Roket ana kartından (UKB)
        self.irtifa: float = 0.0

        # GPS Verileri - Ana Roket (saf float)
        self.roket_gps_irtifa: float = 0.0
        self.roket_enlem: float = 0.0
        self.roket_boylam: float = 0.0

        # GPS Verileri - Görev Yükü (saf float)
        self.gorev_gps_irtifa: float = 0.0
        self.gorev_enlem: float = 0.0
        self.gorev_boylam: float = 0.0

        # Görev Yükü Ortam Verileri (BME280)
        # Byte 34-37: Basınç (Pa)
        self.gorev_basinc: float = 0.0
        # Byte 38-41: Sıcaklık (°C)
        self.gorev_sicaklik: float = 0.0
        # Barometrik formülle hesaplanan irtifa (m)
        self.gorev_hesaplanan_irtifa: float = 0.0
        # Basınç ve sıcaklıktan hesaplanan hava yoğunluğu (kg/m³)
        self.gorev_hava_yogunlugu: float = 0.0

        # IMU Verileri (saf float)
        self.jiroskop_x: float = 0.0
        self.jiroskop_y: float = 0.0
        self.jiroskop_z: float = 0.0
        self.ivme_x: float = 0.0
        self.ivme_y: float = 0.0
        self.ivme_z: float = 0.0
        self.aci: float = 0.0

        # Durum
        self.durum: int = 0
        self.durum_text: str = ""

        # Checksum
        self.checksum: int = 0

    # --- Formatlama Metotları ---

    def get_formatted_irtifa(self) -> str:
        """İrtifa değerini formatlanmış string olarak döndürür."""
        return f"{self.irtifa:.2f} m"

    def get_formatted_gps_irtifa(self, value: float) -> str:
        """GPS irtifa değerini formatlanmış string olarak döndürür."""
        return f"{value:.2f} m"

    def get_formatted_coordinate(self, value: float) -> str:
        """Koordinat değerini formatlanmış string olarak döndürür."""
        return f"{value:.6f}°"

    def get_formatted_gyro(self, value: float) -> str:
        """Jiroskop değerini formatlanmış string olarak döndürür."""
        return f"{value:.2f}°/s"

    def get_formatted_accel(self, value: float) -> str:
        """İvme değerini formatlanmış string olarak döndürür."""
        return f"{value:.2f} G"

    def get_formatted_angle(self, value: float) -> str:
        """Açı değerini formatlanmış string olarak döndürür."""
        return f"{value:.2f}°"

    def get_formatted_pressure(self) -> str:
        """Basınç değerini formatlanmış string olarak döndürür (Pa)."""
        return f"{self.gorev_basinc:.1f} Pa"

    def get_formatted_temperature(self) -> str:
        """Sıcaklık değerini formatlanmış string olarak döndürür (°C)."""
        return f"{self.gorev_sicaklik:.1f} °C"

    def get_formatted_humidity(self) -> str:
        """Nem değerini formatlanmış string olarak döndürür (%)."""
        return f"% {self.nem}"

    def get_formatted_calculated_altitude(self) -> str:
        """Hesaplanan barometrik irtifayı formatlanmış string olarak döndürür."""
        return f"{self.gorev_hesaplanan_irtifa:.2f} m"

    def get_formatted_density(self) -> str:
        """Hesaplanan hava yoğunluğunu formatlanmış string olarak döndürür."""
        return f"{self.gorev_hava_yogunlugu:.4f} kg/m³"


class DataParser:
    """
    Binary protokol formatındaki telemetri verisini parse eder.
    main.c'deki paketle_gonder() fonksiyonuna göre güncellenmiştir.

    Protokol yapısı (78 byte):
    - Header (0-3): 0xFF, 0xFF, 0x54, 0x52
    - Nem (4): UINT8 (Takım ID yerine nem yazılıyor - main.c L150)
    - Sayaç (5): UINT8
    - Payload (6-73): Float32 değerler (Little Endian)
        - [6-9]   İrtifa (UKB[0-3])
        - [10-13] Roket GPS İrtifa (UKB[4-7])
        - [14-17] Roket Enlem (UKB[8-11])
        - [18-21] Roket Boylam (UKB[12-15])
        - [22-25] Görev Yükü GPS İrtifa (Gorev[4-7])
        - [26-29] Görev Yükü Enlem (Gorev[8-11])
        - [30-33] Görev Yükü Boylam (Gorev[12-15])
        - [34-37] GY BME280 Basınç/Pa (Gorev[0-3]) - main.c L134-135
        - [38-41] GY Sıcaklık/°C (Gorev[16-19]) - main.c L146-147
        - [42-45] Kullanılmıyor (0.0)
        - [46-49] Jiroskop X (UKB[16-19])
        - [50-53] Jiroskop Y (UKB[20-23])
        - [54-57] Jiroskop Z (UKB[24-27])
        - [58-61] İvme X (UKB[28-31])
        - [62-65] İvme Y (UKB[32-35])
        - [66-69] İvme Z (UKB[36-39])
        - [70-73] Açı (UKB[40-43])
    - Durum (74): UINT8
    - Checksum (75): Byte 4-74 arası toplamın mod 256
    - Footer (76-77): 0x0D, 0x0A
    """

    # Header bytes
    HEADER = bytes([0xFF, 0xFF, 0x54, 0x52])
    # Footer bytes
    FOOTER = bytes([0x0D, 0x0A])
    # Paket boyutu
    PACKET_SIZE = 78

    # Durum kod çevirileri
    DURUM_MAP = {
        0: "Beklemede",
        1: "Yükseliyor",
        2: "Tepe Noktası",
        3: "İniş"
    }

    # Barometrik irtifa formül sabitleri
    # h = (T0 / L) * [1 - (P / P0)^(R * L / (g * M))]
    _T0 = 288.15     # Deniz seviyesinde sıcaklık (K)
    _L  = 0.0065     # Sıcaklık azalım oranı (K/m)
    _P0 = 1013.25    # Deniz seviyesi standart basınç (hPa)
    _R  = 8.31432    # Evrensel gaz sabiti (J/(mol·K))
    _g  = 9.80665    # Yerçekimi ivmesi (m/s²)
    _M  = 0.0289644  # Havanın mol kütlesi (kg/mol)
    # Üs değeri (R * L) / (g * M) — sabit olduğu için önceden hesapla
    _EXP = (_R * _L) / (_g * _M)

    @staticmethod
    def _calculate_barometric_altitude(basinc_pa: float, sicaklik_c: float) -> float:
        """
        Barometrik irtifa formülüyle görev yükü irtifasını hesaplar.

        Formül: h = (T0 / L) * [1 - (P_hPa / P0)^(R*L / g*M)]

        Args:
            basinc_pa: Basınç değeri (Pascal)
            sicaklik_c: Sıcaklık değeri (°C) - formülde kullanılmıyor
                        ancak ileride gelişmiş hesaplamalar için tutulabilir.

        Returns:
            float: Hesaplanan irtifa (metre). Hata durumunda 0.0.
        """
        try:
            # Pascal -> hPa dönüşümü (P0 hPa cinsinden)
            basinc_hpa = basinc_pa / 100.0

            # Sıfır veya negatif basınç koruması
            if basinc_hpa <= 0:
                return 0.0

            # h = (T0 / L) * [1 - (P / P0)^exp]
            irtifa = (DataParser._T0 / DataParser._L) * (
                1.0 - math.pow(basinc_hpa / DataParser._P0, DataParser._EXP)
            )
            return max(0.0, irtifa)  # Negatif irtifa döndürme
        except (ValueError, ZeroDivisionError, OverflowError):
            return 0.0

    @staticmethod
    def parse(raw_data: bytes) -> Optional[TelemetryData]:
        """
        Binary formatındaki veriyi parse eder.

        Args:
            raw_data: Binary formatında ham veri (78 byte)

        Returns:
            TelemetryData nesnesi veya hata durumunda None
        """
        try:
            # Paket boyutu kontrolü
            if len(raw_data) != DataParser.PACKET_SIZE:
                print(f"Parse hatası: Yanlış paket boyutu ({len(raw_data)}/{DataParser.PACKET_SIZE})")
                return None

            # Header kontrolü
            if raw_data[0:4] != DataParser.HEADER:
                print(f"Parse hatası: Geçersiz header. Beklenen: {DataParser.HEADER.hex()}, Alınan: {raw_data[0:4].hex()}")
                return None

            # Footer kontrolü
            if raw_data[76:78] != DataParser.FOOTER:
                print(f"Parse hatası: Geçersiz footer. Beklenen: {DataParser.FOOTER.hex()}, Alınan: {raw_data[76:78].hex()}")
                return None

            # Checksum kontrolü
            calculated_checksum = sum(raw_data[4:75]) % 256
            received_checksum = raw_data[75]
            if calculated_checksum != received_checksum:
                print(f"Parse hatası: Checksum uyuşmazlığı. Hesaplanan: {calculated_checksum}, Alınan: {received_checksum}")
                return None

            data = TelemetryData()

            # Nem (Byte 4) - main.c L150: TAKIM ID yerine nem yazılıyor
            data.nem = raw_data[4]

            # Sayaç (Byte 5)
            data.sayac = raw_data[5]

            # Payload (Byte 6-73): Float32 değerler (Little Endian)
            offset = 6

            # İrtifa [6-9] - UKB[0-3]
            data.irtifa = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Roket GPS İrtifa [10-13] - UKB[4-7]
            data.roket_gps_irtifa = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Roket Enlem [14-17] - UKB[8-11]
            data.roket_enlem = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Roket Boylam [18-21] - UKB[12-15]
            data.roket_boylam = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Görev Yükü GPS İrtifa [22-25] - Gorev[4-7]
            data.gorev_gps_irtifa = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Görev Yükü Enlem [26-29] - Gorev[8-11]
            data.gorev_enlem = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Görev Yükü Boylam [30-33] - Gorev[12-15]
            data.gorev_boylam = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # GY BME280 Basınç [34-37] - Gorev[0-3] (main.c L134-135: "kademe irtifaya yaziliyor")
            data.gorev_basinc = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # GY Sıcaklık [38-41] - Gorev[16-19] (main.c L146-147: "kademe enleme yaziliyor")
            data.gorev_sicaklik = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # [42-45] Kullanılmıyor (Eski Kademe Boylam slotu, main.c'de yazılmıyor)
            offset += 4

            # Jiroskop X [46-49] - UKB[16-19]
            data.jiroskop_x = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Jiroskop Y [50-53] - UKB[20-23]
            data.jiroskop_y = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Jiroskop Z [54-57] - UKB[24-27]
            data.jiroskop_z = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # İvme X [58-61] - UKB[28-31]
            data.ivme_x = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # İvme Y [62-65] - UKB[32-35]
            data.ivme_y = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # İvme Z [66-69] - UKB[36-39]
            data.ivme_z = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Açı [70-73] - UKB[40-43]
            data.aci = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4

            # Durum (Byte 74) - UKB[44]
            data.durum = raw_data[74]
            data.durum_text = DataParser.DURUM_MAP.get(data.durum, str(data.durum))

            # Checksum (Byte 75)
            data.checksum = received_checksum

            # Barometrik irtifa hesapla (Görev Yükü için)
            data.gorev_hesaplanan_irtifa = DataParser._calculate_barometric_altitude(
                data.gorev_basinc, data.gorev_sicaklik
            )

            # Hava yoğunluğunu hesapla: rho = P / (R * T)
            # R_hava = 287.0 J/(kg·K)
            # T_kelvin = T_celsius + 273.15
            t_kelvin = data.gorev_sicaklik + 273.15
            if t_kelvin <= 0:
                data.gorev_hava_yogunlugu = 0.0
            else:
                data.gorev_hava_yogunlugu = data.gorev_basinc / (287.0 * t_kelvin)

            return data

        except struct.error as e:
            print(f"Veri parse hatası (struct): {e}")
            return None
        except Exception as e:
            print(f"Veri parse hatası: {e}")
            return None

    @staticmethod
    def get_durum_text(durum_code: int) -> str:
        """
        Durum kodunu açıklama metnine çevirir.

        Args:
            durum_code: Durum kodu (0-3)

        Returns:
            Durum açıklama metni
        """
        return DataParser.DURUM_MAP.get(durum_code, str(durum_code))
