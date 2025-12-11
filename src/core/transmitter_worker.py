# transmitter_worker.py
# Seri port yazma işlemleri için Worker sınıfı
# Binary protokol formatında (78 byte) veri gönderir

import serial
import queue
import time
from PyQt6.QtCore import QObject, pyqtSignal


class TransmitterWorker(QObject):
    """
    GUI'yi bloke etmemek için ayrı bir thread'de seri port yazması yapar.
    Binary protokol formatında (78 byte) paketler gönderir.
    """
    # GUI thread'ine göndermek için sinyaller
    transmission_error = pyqtSignal(str)  # Hata mesajı gönderir
    finished = pyqtSignal()                # Thread bittiğinde sinyal verir
    
    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.port = port
        self.baudrate = baudrate
        self.is_running = False
        self.ser = None
        self.data_queue = queue.Queue(maxsize=1000)  # Toleransı artırmak için 1000 paket tampon
    
    def run(self):
        """
        Thread başlatıldığında çalışacak ana fonksiyon.
        """
        self.is_running = True
        
        try:
            # write_timeout ekleyerek yazma işleminin bloklanmasını önle
            # dsrdtr=False: Donanım akış kontrolünü devre dışı bırak (bazen buffer sorununa yol açar)
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1, write_timeout=1, dsrdtr=False)
            print(f"TransmitterWorker: {self.port} portu açıldı.")
        except serial.SerialException as e:
            self.transmission_error.emit(f"Verici port açılamadı: {e}")
            self.is_running = False
            self.finished.emit()
            return
        
        while self.is_running:
            try:
                # Kuyruktan veri al (timeout ile)
                try:
                    data = self.data_queue.get(timeout=0.1)
                    
                    # Veriyi gönder
                    if self.ser and self.ser.is_open:
                        self.ser.write(data)
                        self.ser.flush()  # Buffer'ı zorla boşalt (anlık iletim için)
                        # Debug: Gönderilen veri bilgisi
                        # print(f"TransmitterWorker: {len(data)} byte gönderildi.")
                    
                    self.data_queue.task_done()
                    
                except queue.Empty:
                    # Kuyrukta veri yoksa devam et
                    continue
                
            except serial.SerialException as e:
                # Cihaz çıkarılırsa vb.
                self.transmission_error.emit(f"Verici port hatası: {e}")
                self.is_running = False
            
            # Ana thread'den (GUI) durdurma sinyali gelirse döngüden çık
            if not self.is_running:
                break
        
        # Döngü bittiğinde portu kapat
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"TransmitterWorker: {self.port} portu kapatıldı.")
        
        self.finished.emit()
    
    def send_data(self, data: bytes):
        """
        Veriyi gönderim kuyruğuna ekler.
        Thread-safe olarak çalışır.
        Kuyruk doluysa eski veriyi atar (non-blocking).
        
        Args:
            data: Gönderilecek binary veri (78 byte paket)
        """
        if self.is_running:
            try:
                # Non-blocking put - kuyruk doluysa hata fırlatır
                self.data_queue.put_nowait(data)
            except queue.Full:
                # Kuyruk doluysa en eski veriyi at ve yeniyi ekle
                try:
                    self.data_queue.get_nowait()
                    self.data_queue.put_nowait(data)
                    print("TransmitterWorker: Kuyruk dolu, eski paket atıldı.")
                except:
                    pass  # Hata durumunda sessizce devam et
    
    def stop(self):
        """
        Thread'in güvenli bir şekilde durdurulması için 'is_running' flag'ını ayarlar.
        """
        self.is_running = False
        # Kuyruğu temizle
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
                self.data_queue.task_done()
            except queue.Empty:
                break
        print("TransmitterWorker: Durdurma sinyali alındı.")
