# csv_logger.py
# Telemetri verilerini CSV dosyasına kaydeder.

import os
import csv
from datetime import datetime
from .data_parser import TelemetryData

class CSVLogger:
    """
    Telemetri verilerini CSV formatında dosyaya kaydeder.
    Her oturum için 'logs/' klasöründe tarih-saat etiketli yeni bir dosya oluşturur.
    """
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.file = None
        self.writer = None
        self.filename = None
        self.is_active = False
        
        # Log klasörünü oluştur
        if not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir)
            except OSError as e:
                print(f"Log klasörü oluşturulamadı: {e}")

    def start_logging(self):
        """
        Yeni bir log dosyası oluşturur ve yazmaya başlar.
        """
        if self.is_active:
            return

        try:
            # Dosya adı: telemetry_YYYYMMDD_HHMMSS.csv
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = os.path.join(self.log_dir, f"telemetry_{timestamp}.csv")
            
            # Dosyayı aç (newline='' csv modülü için gerekli)
            self.file = open(self.filename, 'w', newline='', encoding='utf-8')
            self.writer = csv.writer(self.file)
            
            # Başlık satırını yaz
            headers = [
                "Zaman", "TakimID", "Sayac", "Irtifa", 
                "Roket_GPS_Irtifa", "Roket_Enlem", "Roket_Boylam",
                "Gorev_GPS_Irtifa", "Gorev_Enlem", "Gorev_Boylam",
                "Kademe_GPS_Irtifa", "Kademe_Enlem", "Kademe_Boylam",
                "Jiro_X", "Jiro_Y", "Jiro_Z",
                "Ivme_X", "Ivme_Y", "Ivme_Z",
                "Aci", "Durum", "Durum_Metin", "Checksum"
            ]
            self.writer.writerow(headers)
            self.file.flush()
            
            self.is_active = True
            print(f"Loglama başlatıldı: {self.filename}")
            
        except Exception as e:
            print(f"Log dosyası oluşturma hatası: {e}")
            self.is_active = False

    def log(self, data: TelemetryData):
        """
        Gelen telemetri verisini dosyaya yazar.
        
        Args:
            data: TelemetryData nesnesi
        """
        if not self.is_active or not self.writer:
            return
            
        try:
            # Şu anki zaman
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            row = [
                current_time,
                data.takim_id,
                data.sayac,
                f"{data.irtifa:.2f}",
                f"{data.roket_gps_irtifa:.2f}",
                f"{data.roket_enlem:.6f}",
                f"{data.roket_boylam:.6f}",
                f"{data.gorev_gps_irtifa:.2f}",
                f"{data.gorev_enlem:.6f}",
                f"{data.gorev_boylam:.6f}",
                f"{data.kademe_gps_irtifa:.2f}",
                f"{data.kademe_enlem:.6f}",
                f"{data.kademe_boylam:.6f}",
                f"{data.jiroskop_x:.2f}",
                f"{data.jiroskop_y:.2f}",
                f"{data.jiroskop_z:.2f}",
                f"{data.ivme_x:.2f}",
                f"{data.ivme_y:.2f}",
                f"{data.ivme_z:.2f}",
                f"{data.aci:.2f}",
                data.durum,
                data.durum_text,
                data.checksum
            ]
            
            self.writer.writerow(row)
            self.file.flush() # Verinin diske yazıldığından emin ol
            
        except Exception as e:
            print(f"Log yazma hatası: {e}")

    def stop_logging(self):
        """
        Loglamayı durdurur ve dosyayı kapatır.
        """
        if self.file:
            try:
                self.file.close()
                print(f"Loglama durduruldu: {self.filename}")
            except Exception as e:
                print(f"Dosya kapatma hatası: {e}")
            finally:
                self.file = None
                self.writer = None
                self.is_active = False
