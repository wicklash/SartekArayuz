# data_parser.py
# Telemetri verisi parse mantığı

from typing import Dict, Optional, Tuple


class TelemetryData:
    """Telemetri veri modeli"""
    
    def __init__(self):
        self.takim_id: str = ""
        self.sayac: str = ""
        self.irtifa: str = ""
        self.roket_gps_irtifa: str = ""
        self.roket_enlem: str = ""
        self.roket_boylam: str = ""
        self.gorev_gps_irtifa: str = ""
        self.gorev_enlem: str = ""
        self.gorev_boylam: str = ""
        self.kademe_gps_irtifa: str = ""
        self.kademe_enlem: str = ""
        self.kademe_boylam: str = ""
        self.jiroskop_x: str = ""
        self.jiroskop_y: str = ""
        self.jiroskop_z: str = ""
        self.ivme_x: str = ""
        self.ivme_y: str = ""
        self.ivme_z: str = ""
        self.aci: str = ""
        self.durum: str = ""
        self.durum_text: str = ""
        self.crc: str = ""


class DataParser:
    """
    CSV formatındaki telemetri verisini parse eder.
    Format: TAKIM_ID,SAYAC,IRTIFA,ROKET_GPS_IRT,ROKET_ENLEM,ROKET_BOYLAM,
            GOREV_GPS_IRT,GOREV_ENLEM,GOREV_BOYLAM,KADEME_GPS_IRT,KADEME_ENLEM,KADEME_BOYLAM,
            JIRO_X,JIRO_Y,JIRO_Z,IVME_X,IVME_Y,IVME_Z,ACI,DURUM,CRC
    """
    
    # Durum kod çevirileri
    DURUM_MAP = {
        "0": "Beklemede",
        "1": "Yükseliyor",
        "2": "Tepe Noktası",
        "3": "İniş"
    }
    
    @staticmethod
    def parse(raw_data: str) -> Optional[TelemetryData]:
        """
        CSV formatındaki veriyi parse eder.
        
        Args:
            raw_data: CSV formatında ham veri
            
        Returns:
            TelemetryData nesnesi veya hata durumunda None
        """
        try:
            parts = raw_data.split(',')
            
            if len(parts) < 21:
                print(f"Parse hatası: Yetersiz veri alanı ({len(parts)}/21)")
                return None
            
            data = TelemetryData()
            
            # Veri alanlarını doldur
            data.takim_id = parts[0]
            data.sayac = parts[1]
            data.irtifa = f"{parts[2]} m"
            data.roket_gps_irtifa = f"{parts[3]} m"
            data.roket_enlem = f"{parts[4]}°"
            data.roket_boylam = f"{parts[5]}°"
            data.gorev_gps_irtifa = f"{parts[6]} m"
            data.gorev_enlem = f"{parts[7]}°"
            data.gorev_boylam = f"{parts[8]}°"
            data.kademe_gps_irtifa = f"{parts[9]} m"
            data.kademe_enlem = f"{parts[10]}°"
            data.kademe_boylam = f"{parts[11]}°"
            data.jiroskop_x = f"{parts[12]}°/s"
            data.jiroskop_y = f"{parts[13]}°/s"
            data.jiroskop_z = f"{parts[14]}°/s"
            data.ivme_x = f"{parts[15]} G"
            data.ivme_y = f"{parts[16]} G"
            data.ivme_z = f"{parts[17]} G"
            data.aci = f"{parts[18]}°"
            data.durum = parts[19]
            data.durum_text = DataParser.DURUM_MAP.get(parts[19], parts[19])
            data.crc = parts[20]
            
            return data
            
        except Exception as e:
            print(f"Veri parse hatası: {e}")
            print(f"Ham veri: {raw_data}")
            return None
    
    @staticmethod
    def get_durum_text(durum_code: str) -> str:
        """
        Durum kodunu açıklama metnine çevirir.
        
        Args:
            durum_code: Durum kodu (0-3)
            
        Returns:
            Durum açıklama metni
        """
        return DataParser.DURUM_MAP.get(durum_code, durum_code)
