# data_parser.py
# Telemetri verisi parse mantığı
# Binary protokol formatını parse eder (78 byte)

import struct
from typing import Optional


class TelemetryData:
    """
    Telemetri veri modeli.
    Veriler saf sayı (float/int) olarak tutulur.
    Birim ekleme işi UI katmanında yapılır (performans için).
    """
    
    def __init__(self):
        # Kimlik ve sayaç
        self.takim_id: int = 0
        self.sayac: int = 0
        
        # İrtifa (saf float)
        self.irtifa: float = 0.0
        
        # GPS Verileri - Ana Roket (saf float)
        self.roket_gps_irtifa: float = 0.0
        self.roket_enlem: float = 0.0
        self.roket_boylam: float = 0.0
        
        # GPS Verileri - Görev Yükü (saf float)
        self.gorev_gps_irtifa: float = 0.0
        self.gorev_enlem: float = 0.0
        self.gorev_boylam: float = 0.0
        
        # GPS Verileri - Kademe (saf float)
        self.kademe_gps_irtifa: float = 0.0
        self.kademe_enlem: float = 0.0
        self.kademe_boylam: float = 0.0
        
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


class DataParser:
    """
    Binary protokol formatındaki telemetri verisini parse eder.
    Protokol yapısı (EK-7):
    - Header (0-3): 0xFF, 0xFF, 0x54, 0x52
    - Takım ID (4): UINT8
    - Sayaç (5): UINT8
    - Payload (6-73): 17 adet Float32 (Little Endian)
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
            
            # Takım ID (Byte 4)
            data.takim_id = raw_data[4]
            
            # Sayaç (Byte 5)
            data.sayac = raw_data[5]
            
            # Payload (Byte 6-73): Float32 değerler (Little Endian)
            offset = 6
            
            # İrtifa
            data.irtifa = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            
            # Roket GPS
            data.roket_gps_irtifa = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.roket_enlem = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.roket_boylam = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            
            # Görev Yükü GPS
            data.gorev_gps_irtifa = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.gorev_enlem = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.gorev_boylam = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            
            # Kademe GPS
            data.kademe_gps_irtifa = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.kademe_enlem = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.kademe_boylam = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            
            # IMU - Jiroskop
            data.jiroskop_x = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.jiroskop_y = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.jiroskop_z = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            
            # IMU - İvme
            data.ivme_x = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.ivme_y = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            data.ivme_z = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            
            # Açı
            data.aci = struct.unpack('<f', raw_data[offset:offset+4])[0]
            offset += 4
            
            # Durum (Byte 74)
            data.durum = raw_data[74]
            data.durum_text = DataParser.DURUM_MAP.get(data.durum, str(data.durum))
            
            # Checksum (Byte 75)
            data.checksum = received_checksum
            
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
