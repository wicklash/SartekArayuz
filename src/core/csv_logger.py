# csv_logger.py
# Telemetri verilerini CSV dosyasına kaydeder.

import os
import csv
import threading
import queue
from datetime import datetime
from .data_parser import TelemetryData

class CSVLogger:
    """
    Telemetri verilerini CSV formatında dosyaya kaydeder.
    
    PERFORMANS OPTİMİZASYONU:
    Dosya yazma işlemi ana thread'i (UI) bloklamamak için
    ayrı bir thread üzerinde ve Queue kullanılarak yapılır.
    """
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.file = None
        self.writer = None
        self.filename = None
        self.is_active = False
        
        # Threading ve Queue yapısı
        self.log_queue = queue.Queue()
        self.write_thread = None
        self.stop_event = threading.Event()
        
        # Log klasörünü oluştur
        if not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir)
            except OSError as e:
                print(f"Log klasörü oluşturulamadı: {e}")

    def start_logging(self):
        """
        Yeni bir log dosyası oluşturur ve yazma thread'ini başlatır.
        """
        if self.is_active:
            return

        try:
            # Dosya adı: telemetry_YYYYMMDD_HHMMSS.csv
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = os.path.join(self.log_dir, f"telemetry_{timestamp}.csv")
            
            # Dosyayı aç
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
            
            # Thread başlat
            self.stop_event.clear()
            self.write_thread = threading.Thread(target=self._write_loop, daemon=True)
            self.write_thread.start()
            
            print(f"Loglama başlatıldı (Thread): {self.filename}")
            
        except Exception as e:
            print(f"Log dosyası oluşturma hatası: {e}")
            self.is_active = False

    def log(self, data: TelemetryData):
        """
        Gelen telemetri verisini kuyruğa ekler (Non-blocking).
        
        Args:
            data: TelemetryData nesnesi
        """
        if not self.is_active:
            return
            
        # Veriyi kuyruğa at, işlem hemen döner
        self.log_queue.put(data)

    def _write_loop(self):
        """
        Arka planda çalışan thread fonksiyonu.
        Kuyruktaki verileri dosyaya yazar.
        """
        while not self.stop_event.is_set() or not self.log_queue.empty():
            try:
                # Kuyruktan veri al (timeout ile bekle ki stop_event kontrol edilebilsin)
                try:
                    data = self.log_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Veriyi işle ve yaz
                self._write_to_file(data)
                self.log_queue.task_done()
                
            except Exception as e:
                print(f"Log thread hatası: {e}")
    
    def _write_to_file(self, data: TelemetryData):
        """
        Tek bir veri satırını dosyaya yazar.
        """
        if not self.writer or not self.file:
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
            # Her satırdan sonra flush, veri kaybını önler ama performans maliyeti vardır.
            # Thread içinde olduğumuz için UI bloklanmaz, güvenle kullanabiliriz.
            self.file.flush()
            
        except Exception as e:
            print(f"Dosya yazma hatası: {e}")

    def stop_logging(self):
        """
        Loglamayı durdurur, kalan kuyruğu boşaltır ve dosyayı kapatır.
        """
        if not self.is_active:
            return

        print("Loglama durduruluyor, kuyruk boşaltılıyor...")
        
        # Thread'i durdurma sinyali ver
        self.stop_event.set()
        
        # Thread'in bitmesini bekle
        if self.write_thread:
            self.write_thread.join(timeout=2.0)
        
        # Dosyayı kapat
        if self.file:
            try:
                self.file.close()
                print(f"Loglama tamamlandı: {self.filename}")
            except Exception as e:
                print(f"Dosya kapatma hatası: {e}")
            finally:
                self.file = None
                self.writer = None
                self.is_active = False
