# serial_worker.py
# Seri port okuma işlemleri için Worker sınıfı
# Binary protokol formatında (78 byte) veri okur

import serial
from PyQt6.QtCore import QObject, pyqtSignal


class SerialWorker(QObject):
    """
    GUI'yi bloke etmemek için ayrı bir thread'de seri port okuması yapar.
    Binary protokol formatında (78 byte) paketler okur.
    """
    # GUI thread'ine göndermek için sinyaller
    data_received = pyqtSignal(bytes)  # Gelen veriyi (bytes) gönderir
    port_error = pyqtSignal(str)       # Hata mesajı gönderir
    finished = pyqtSignal()             # Thread bittiğinde sinyal verir

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.is_running = False
        self.ser = None
        self.buffer = bytearray()  # Gelen verileri buffer'da biriktir
        self.PACKET_SIZE = 78
        self.HEADER = bytes([0xFF, 0xFF, 0x54, 0x52])

    def run(self):
        """
        Thread başlatıldığında çalışacak ana fonksiyon.
        """
        self.is_running = True
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Worker: {self.port} portu açıldı.")
        except serial.SerialException as e:
            self.port_error.emit(f"Port açılamadı: {e}")
            self.is_running = False
            self.finished.emit()
            return

        while self.is_running:
            try:
                if self.ser.in_waiting > 0:
                    # Gelen byte'ları oku
                    new_data = self.ser.read(self.ser.in_waiting)
                    self.buffer.extend(new_data)
                    
                    # Buffer'dan paketleri çıkar
                    self._extract_packets()
                
            except serial.SerialException as e:
                # Cihaz çıkarılırsa vb.
                self.port_error.emit(f"Seri port hatası: {e}")
                self.is_running = False
            
            # Ana thread'den (GUI) durdurma sinyali gelirse döngüden çık
            if not self.is_running:
                break
        
        # Döngü bittiğinde portu kapat
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Worker: {self.port} portu kapatıldı.")
        
        self.finished.emit()
    
    def _extract_packets(self):
        """
        Buffer'dan 78 byte'lık paketleri çıkarır ve sinyal gönderir.
        Header (0xFF, 0xFF, 0x54, 0x52) ile paket başlangıcını tespit eder.
        """
        while len(self.buffer) >= self.PACKET_SIZE:
            # Header'ı ara
            header_index = -1
            for i in range(len(self.buffer) - 3):
                if (self.buffer[i] == 0xFF and 
                    self.buffer[i+1] == 0xFF and 
                    self.buffer[i+2] == 0x54 and 
                    self.buffer[i+3] == 0x52):
                    header_index = i
                    break
            
            if header_index == -1:
                # Header bulunamadı, buffer'ı temizle (ilk byte'ı atla)
                if len(self.buffer) > 0:
                    self.buffer.pop(0)
                break
            
            # Header'dan önceki verileri atla
            if header_index > 0:
                self.buffer = self.buffer[header_index:]
            
            # Yeterli veri var mı kontrol et
            if len(self.buffer) < self.PACKET_SIZE:
                break
            
            # Paketi çıkar
            packet = bytes(self.buffer[:self.PACKET_SIZE])
            self.buffer = self.buffer[self.PACKET_SIZE:]
            
            # Paketi GUI'ye gönder
            self.data_received.emit(packet)
    
    def stop(self):
        """
        Thread'in güvenli bir şekilde durdurulması için 'is_running' flag'ını ayarlar.
        """
        self.is_running = False
        self.buffer.clear()
        print("Worker: Durdurma sinyali alındı.")
