# serial_worker.py
# Seri port okuma işlemleri için Worker sınıfı

import serial
from PyQt6.QtCore import QObject, pyqtSignal


class SerialWorker(QObject):
    """
    GUI'yi bloke etmemek için ayrı bir thread'de seri port okuması yapar.
    """
    # GUI thread'ine göndermek için sinyaller
    data_received = pyqtSignal(str)  # Gelen veriyi (string) gönderir
    port_error = pyqtSignal(str)     # Hata mesajı gönderir
    finished = pyqtSignal()          # Thread bittiğinde sinyal verir

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.is_running = False
        self.ser = None

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
                # ser.readline() burada bekler (timeout=1 saniye)
                # GUI thread'ini bloke etmez, çünkü bu 'run' metodu
                # ayrı bir QThread'de çalışır.
                if self.ser.in_waiting > 0:
                    line_bytes = self.ser.readline()
                    
                    # Gelen byte'ları UTF-8 string'e çevir
                    try:
                        line_str = line_bytes.decode('utf-8').strip()
                        if line_str:
                            # Veri alındıysa, GUI'ye sinyal gönder
                            self.data_received.emit(line_str)
                    except UnicodeDecodeError:
                        # Hatalı veri gelirse (örn: bağlantı yeni kurulurken)
                        print("Worker: Hatalı byte dizisi alındı, atlanıyor.")

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

    def stop(self):
        """
        Thread'in güvenli bir şekilde durdurulması için 'is_running' flag'ını ayarlar.
        """
        self.is_running = False
        print("Worker: Durdurma sinyali alındı.")
