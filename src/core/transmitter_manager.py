# transmitter_manager.py
# Thread yönetimi ve verici port bağlantı kontrolü

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from .transmitter_worker import TransmitterWorker


class TransmitterManager(QObject):
    """
    Verici port bağlantısını ve thread yaşam döngüsünü yönetir.
    UI'dan iş mantığını ayırır.
    """
    # UI'ye gönderilecek sinyaller
    transmission_error = pyqtSignal(str)     # Gönderim hatası
    transmission_started = pyqtSignal()      # Gönderim başladı
    transmission_stopped = pyqtSignal()      # Gönderim durduruldu
    
    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.transmitter_thread = None
        self.transmitter_worker = None
    
    def set_port(self, port):
        """
        Port'u dinamik olarak ayarlar.
        
        Args:
            port: Port adı (örn: 'COM10')
        """
        self.port = port
    
    def start_transmission(self):
        """
        Verici port bağlantısını başlatır.
        """
        if self.transmitter_thread and self.transmitter_thread.isRunning():
            print("Verici bağlantı zaten aktif!")
            return
        
        if not self.port:
            error_msg = "Verici port seçilmedi!"
            print(f"Hata: {error_msg}")
            self.transmission_error.emit(error_msg)
            return
        
        print(f"{self.port} verici portuna {self.baudrate} baud ile bağlanılıyor...")
        
        # Thread ve Worker oluştur
        self.transmitter_thread = QThread()
        self.transmitter_worker = TransmitterWorker(port=self.port, baudrate=self.baudrate)
        
        # Worker'ı thread'e taşı
        self.transmitter_worker.moveToThread(self.transmitter_thread)
        
        # Sinyal bağlantıları - Worker'dan Manager'a
        self.transmitter_worker.transmission_error.connect(self._on_transmission_error)
        
        # Thread yaşam döngüsü
        self.transmitter_thread.started.connect(self.transmitter_worker.run)
        self.transmitter_worker.finished.connect(self.transmitter_thread.quit)
        self.transmitter_worker.finished.connect(self.transmitter_worker.deleteLater)
        self.transmitter_thread.finished.connect(self.transmitter_thread.deleteLater)
        self.transmitter_thread.finished.connect(self._on_thread_finished)
        
        # Thread'i başlat
        self.transmitter_thread.start()
        self.transmission_started.emit()
    
    def stop_transmission(self):
        """
        Verici port bağlantısını durdurur.
        """
        if self.transmitter_worker:
            self.transmitter_worker.stop()
            print("Verici bağlantı kesiliyor...")
        else:
            print("Aktif verici bağlantı yok.")
    
    def is_transmitting(self):
        """
        Verici bağlantının aktif olup olmadığını kontrol eder.
        
        Returns:
            bool: Bağlantı aktifse True, değilse False
        """
        return self.transmitter_thread is not None and self.transmitter_thread.isRunning()
    
    def send_data(self, data: bytes):
        """
        Binary veriyi verici worker'a gönderir.
        
        Args:
            data: Gönderilecek binary veri (78 byte paket)
        """
        if self.transmitter_worker and self.is_transmitting():
            self.transmitter_worker.send_data(data)
    
    def _on_transmission_error(self, error_msg):
        """
        Worker'dan gelen hatayı UI'ye iletir ve bağlantıyı durdurur.
        """
        print(f"TransmitterManager: Hata - {error_msg}")
        self.transmission_error.emit(error_msg)
        self.stop_transmission()
    
    def _on_thread_finished(self):
        """
        Thread durduğunda temizlik yapar.
        """
        print("Verici bağlantı kesildi.")
        self.transmitter_thread = None
        self.transmitter_worker = None
        self.transmission_stopped.emit()
